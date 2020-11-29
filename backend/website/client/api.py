import logging
import concurrent.futures
import pandas as pd
from datetime import datetime
from functools import reduce

from bs4 import BeautifulSoup, SoupStrainer
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests_futures.sessions import FuturesSession
from website.client import exceptions

logger = logging.getLogger(__name__)

session = FuturesSession(max_workers=6)
retries = Retry(total=3, backoff_factor=1.0, status_forcelist=[500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))

payloads = []


def set_credentials(username, password):
    try:
        logger.info("Setting credentials")
        r = session.get(
            "https://clairvia.texaschildrens.org/ClairviaWeb/Login.aspx"
        ).result()
        soup = BeautifulSoup(r.text, "lxml")

        login_form_inputs = [
            ((input.get("name"), input.get("value")))
            for input in soup.find_all("input")
        ]
        login_form_inputs.append(("ctl00$bodyPlaceHolder$Login1$UserName", username))
        login_form_inputs.append(("ctl00$bodyPlaceHolder$Login1$Password", password))
        login_post_data = dict(login_form_inputs)

        r = session.post(
            "https://clairvia.texaschildrens.org/ClairviaWeb/Login.aspx?ReturnUrl=https://clairvia.texaschildrens.org/ClairviaWeb/WebScheduling/Tools/Locator.aspx",
            login_post_data,
        ).result()
        soup = BeautifulSoup(r.text, "lxml")

        employees = soup.find(
            "select",
            id="ctl00_ctl00_ctl00_bodyPlaceHolder_MasterContentPlaceHolder_SchedulingMasterContentPlaceHolder_ddEmployee",
        ).find_all("option")
        employee_ids = [employee.get("value") for employee in employees]

        schedule_form_inputs = [
            ((input.get("id"), input.get("value")))
            for input in soup.find_all("input")
            if input.get("id")
        ]
        schedule_form_inputs.append(
            (
                "ctl00$ctl00$ctl00$bodyPlaceHolder$MasterContentPlaceHolder$SchedulingMasterContentPlaceHolder$btnSearch",
                "Search",
            )
        )
        schedule_post_data = dict(schedule_form_inputs)

        global payloads
        payloads = [
            {
                **schedule_post_data,
                "ctl00$ctl00$ctl00$bodyPlaceHolder$MasterContentPlaceHolder$SchedulingMasterContentPlaceHolder$ddEmployee": id,
            }
            for id in employee_ids
        ]
    except AttributeError:
        logger.error("Unable to login to TCH")
        raise exceptions.InvalidCredentialsError("Unable to login to TCH")


def __response_hook(resp, *args, **kwargs):
    strainer = SoupStrainer(
        "table",
        attrs={
            "id": "ctl00_ctl00_ctl00_bodyPlaceHolder_MasterContentPlaceHolder_SchedulingMasterContentPlaceHolder_gridLocatorResults"
        },
    )
    table = BeautifulSoup(resp.text, "lxml", parse_only=strainer)

    if table is not None:
        table_rows = table.find_all("tr")[1:]
        data_rows = [row.find_all("td") for row in table_rows]
        data = [[cell.string for cell in row] for row in data_rows]
        resp.data = data
    else:
        resp.data = None


def get_schedules(date):
    schedule_payloads = [
        {
            **payload,
            "ctl00$ctl00$ctl00$bodyPlaceHolder$MasterContentPlaceHolder$SchedulingMasterContentPlaceHolder$txtDate": date,
        }
        for payload in payloads
    ]
    logger.info("Getting all employee schedules for date: %s", date)

    futures = [
        session.post(
            "https://clairvia.texaschildrens.org/ClairviaWeb/WebScheduling/Tools/Locator.aspx",
            post_data,
            hooks={"response": __response_hook},
        )
        for post_data in schedule_payloads
    ]
    responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    data = [item for response in responses if response.data for item in response.data]
    df = pd.DataFrame(
        data, columns=["Employee", "Skill", "Assignment", date, "Start", "End"]
    )
    df.drop(["Skill", "Assignment", "Start", "End"], axis=1, inplace=True)

    return df


def __process_df(df):
    headers = df.columns.values.tolist()
    data = df.to_numpy().tolist()
    data.insert(0, headers)

    tasks = df.iloc[:, -1].value_counts().sort_index()
    tasks_names = tasks.index.tolist()
    tasks_counts = tasks.values.tolist()
    metrics = [[task, str(count)] for task, count in zip(tasks_names, tasks_counts)]
    metrics.insert(0, ["Task", "Count"])
    return {"metrics": metrics, "schedules": data}


def get_schedules_for_dates(dates):
    formatted_dates = [
        datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y") for date in dates
    ]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_schedules, date) for date in formatted_dates]
        dfs = [f.result() for f in futures]
        data = [__process_df(df) for df in dfs]
        return {"data": data}
