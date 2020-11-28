<template>
  <b-container>
    <b-row class="vh-100" align-h="center" align-v="center">
      <b-col cols="6">
        <b-form @submit="onSubmit">
          <b-form-group label="Username" label-for="username-input">
            <b-form-input
              v-model="form.username"
              type="text"
              required>
            </b-form-input>
          </b-form-group>
          <b-form-group label="Password" label-for="password-input">
            <b-form-input
              v-model="form.password"
              type="password"
              required>
            </b-form-input>
          </b-form-group>
          <b-button type="submit" class="mx-auto d-block" variant="primary">Submit</b-button>
        </b-form>
      </b-col>
    </b-row>
    <FlashMessage></FlashMessage>
  </b-container>
</template>

<script>
import axios from 'axios';
import Vue from 'vue';
import FlashMessage from '@smartweb/vue-flash-message';

Vue.use(FlashMessage);

export default {
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
    };
  },
  methods: {
    login(payload) {
      const path = '/login';
      axios.post(path, payload, { withCredentials: true })
        .then((res) => {
          const status = JSON.parse(res.status);

          if (status === 200) {
            this.$router.push('/portal');
          } else {
            this.flashMessage.show({
              status: 'error',
              title: 'Unable to log in',
              message: 'Unable to log in. Please try again.',
            });
          }
        })
        .catch(() => this.flashMessage.show({
          status: 'error',
          title: 'Unable to log in',
          message: 'Unable to log in. Please try again.',
        }));
    },
    onSubmit(evt) {
      evt.preventDefault();
      const payload = {
        username: this.form.username,
        password: this.form.password,
      };
      this.login(payload);
    },
  },
};
</script>
