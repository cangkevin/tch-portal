<template>
  <b-container>
    <b-row>
      <b-col>
        <v-calendar
          class="mx-auto mt-3"
          :attributes="attributes"
          @dayclick="onDayClick" />
      </b-col>
    </b-row>

    <b-row>
      <b-col>
        <div class="text-center p-3">
          <b-button
            v-on:click="onSubmit"
            variant="primary"
            :disabled="loading">
            <b-spinner v-if="loading" small></b-spinner>
            {{ buttonText }}
          </b-button>
        </div>
      </b-col>
    </b-row>

    <b-row>
      <b-col v-for="(param, index) in params" :key="index">
        <vue-table-dynamic :params="param"></vue-table-dynamic>
      </b-col>
    </b-row>
    <FlashMessage></FlashMessage>
  </b-container>
</template>

<script>
import axios from 'axios';
import Vue from 'vue';
import VCalendar from 'v-calendar';
import VueTableDynamic from 'vue-table-dynamic';

Vue.use(VCalendar);

export default {
  components: { VueTableDynamic },
  data() {
    return {
      loading: false,
      params: [],
      days: [],
    };
  },
  computed: {
    dates() {
      return this.days.map((day) => day.date);
    },
    attributes() {
      return this.dates.map((date) => ({
        highlight: true,
        dates: date,
      }));
    },
    buttonText() {
      return this.loading ? 'Finding schedules...' : 'Find schedules';
    },
  },
  methods: {
    onDayClick(day) {
      const idx = this.days.findIndex((d) => d.id === day.id);
      if (idx >= 0) {
        this.days.splice(idx, 1);
      } else {
        this.days.push({
          id: day.id,
          date: day.date,
        });
      }
    },
    onSubmit() {
      if (this.days.length > 0) {
        this.loading = true;

        const path = '/schedule';
        axios.post(path, {
          dates: Array.from(this.days, (d) => d.id).sort(),
        }, { withCredentials: true })
          .then((response) => {
            this.params = Array.from(response.data.schedules, (schedule) => (
              {
                data: schedule,
                header: 'row',
                border: true,
                stripe: true,
                enableSearch: true,
                sort: [0, 1],
              }
            ));

            this.loading = false;
          })
          .catch((error) => {
            this.loading = false;
            if (error.response.status === 303) {
              this.$router.push('/');
            } else {
              this.flashMessage.show({
                position: 'top right',
                status: 'error',
                title: 'Unable to fetch schedules',
                message: 'Unable to fetch schedules. Please try again or re-logging in.',
              });
            }
          });
      }
    },
  },
};

</script>
