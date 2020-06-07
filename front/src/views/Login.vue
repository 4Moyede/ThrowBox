<template>
  <v-sheet style="margin-top: 100px">
    <v-row justify="center">
      <v-col xs="10" sm="8" md="6" lg="4" class="mx-4">
        <v-card elevation="0" class="pa-4" outlined>
          <v-tabs
            class="no-transition"
            background-color="#ffffff"
            color="secondary"
            grow
            v-model="tab"
          >
            <v-tab>Login</v-tab>
            <v-tab>Sign Up</v-tab>
          </v-tabs>
          <div class="SignInTitle">
            {{title}}
            <div class="my-2 signInDivider"></div>
          </div>
          <div class="pa-12">
            <ValidationObserver ref="obs" v-slot="{ invalid, validated}">
              <v-form v-if="tab===0">
                <ValidationProvider name="id" rules="required" v-slot="{ errors }">
                  <v-text-field
                    color="secondary"
                    label="ID"
                    v-model="LoginForm.username"
                    :error-messages="errors"
                    clearable
                    filled
                    type="text"
                  ></v-text-field>
                </ValidationProvider>
                <ValidationProvider name="password" rules="required" v-slot="{ errors }">
                  <v-text-field
                    color="secondary"
                    label="Password"
                    ty
                    v-model="LoginForm.password"
                    :error-messages="errors"
                    clearable
                    filled
                    type="password"
                  ></v-text-field>
                </ValidationProvider>
                <v-row justify="end" class="mr-0 mt-n7 mb-7">
                  <v-btn
                    text
                    color="secondary"
                    style="font-weight: 400; text-transform: none"
                    @click="findPassword()"
                  >Forgot Password?</v-btn>
                </v-row>
                <v-row class="mx-0">
                  <v-btn
                    color="secondary"
                    style="margin: auto"
                    block
                    large
                    :disabled="invalid || !validated"
                    @click="Login()"
                  >
                    <div style="font-size: 18px">Login</div>
                  </v-btn>
                </v-row>
              </v-form>
              <v-form v-if="tab===1">
                <ValidationProvider name="id" rules="required|min:4|max:15" v-slot="{ errors }">
                  <v-text-field
                    prepend-inner-icon="mdi-account"
                    v-model="SignUpForm.username"
                    :counter="15"
                    :error-messages="errors"
                    label="ID"
                    color="secondary"
                    type="text"
                  ></v-text-field>
                </ValidationProvider>
                <ValidationProvider
                  name="password"
                  rules="required|min:8|max:30"
                  v-slot="{ errors }"
                >
                  <v-text-field
                    style="margin-top: 5px"
                    prepend-inner-icon="mdi-lock"
                    autocomplete="new-password"
                    v-model="SignUpForm.password"
                    :counter="30"
                    :error-messages="errors"
                    label="Password"
                    color="secondary"
                    type="password"
                  ></v-text-field>
                </ValidationProvider>
                <ValidationProvider
                  name="passwordConfirm"
                  rules="required|min:8|max:30|confirmed:password"
                  v-slot="{ errors }"
                >
                  <v-text-field
                    style="margin-top: 5px"
                    prepend-inner-icon="mdi-lock"
                    autocomplete="new-password"
                    v-model="SignUpForm.passwordConfirm"
                    :error-messages="errors"
                    :counter="30"
                    label="PasswordConfirm"
                    color="secondary"
                    type="password"
                  ></v-text-field>
                </ValidationProvider>
                <ValidationProvider name="email" rules="required|email" v-slot="{ errors }">
                  <v-text-field
                    style="margin-top: 5px; margin-bottom: 10px"
                    prepend-inner-icon="mdi-at"
                    v-model="SignUpForm.email"
                    :error-messages="errors"
                    label="E-mail"
                    autocomplete="email"
                    type="text"
                    color="secondary"
                  ></v-text-field>
                </ValidationProvider>

                <v-btn
                  color="secondary"
                  style="margin: auto; margin-top: 40px"
                  block
                  large
                  @click="SignUp()"
                  :disabled="invalid || !validated"
                >
                  <div style="font-size: 18px">Sign Up</div>
                </v-btn>
              </v-form>
            </ValidationObserver>
          </div>
        </v-card>
      </v-col>
      <!-- email auth dialog -->
      <v-dialog max-width="600" persistent v-model="emailAuthDialog">
        <v-card max-width="600" class="pa-3">
          <div class="dialogTitle">SignUp Confirmation</div>
          <div class="mt-1 mb-4 signInDivider"></div>
          <div class="dialogSubTitle">We sent the confirmation code to the email you entered.</div>
          <div class="dialogSubTitle">Please enter your ID and Code in the form below.</div>
          <ValidationObserver ref="obs" v-slot="{ invalid, validated}">
            <v-form
              style="margin: auto"
              :style="$vuetify.breakpoint.xs ? 'width: 250px' : 'width: 350px'"
            >
              <ValidationProvider name="id" rules="required|min:4|max:15" v-slot="{ errors }">
                <v-text-field
                  prepend-inner-icon="mdi-account"
                  v-model="emailConfirmData.username"
                  :counter="15"
                  :error-messages="errors"
                  label="ID"
                  color="secondary"
                  type="text"
                ></v-text-field>
              </ValidationProvider>
              <ValidationProvider name="id" rules="required|min:4|max:15" v-slot="{ errors }">
                <v-text-field
                  prepend-inner-icon="mdi-lock-clock"
                  v-model="emailConfirmData.confirmationCode"
                  :counter="15"
                  :error-messages="errors"
                  label="Code"
                  color="secondary"
                  type="text"
                ></v-text-field>
              </ValidationProvider>
            </v-form>
            <v-row justify="end" class="mx-0 mt-6">
              <v-btn
                color="secondary"
                @click="emailAuth"
                class="mr-3"
                :disabled="invalid || !validated"
              >Confirm</v-btn>
            </v-row>
          </ValidationObserver>
        </v-card>
      </v-dialog>
      <!--  -->
      <notify
        @clickOk="notifyClickOk"
        :onFlag="resultDialog"
        :message="rtMsg"
      />
      <!--  -->
    </v-row>
  </v-sheet>
</template>

<style scoped>
nav {
  text-align: center;
}
</style>


<script>
import { ValidationProvider, ValidationObserver } from 'vee-validate';
import Notify from '../components/Notify.vue';

export default {
  components: {
    ValidationProvider,
    ValidationObserver,
    Notify,
  },
  data() {
    return {
      title: null,
      LoginForm: {
        username: null,
        password: null,
      },
      SignUpForm: {
        username: null,
        email: null,
        password: null,
        passwordConfirm: null,
      },
      emailConfirmData: {
        username: null,
        confirmationCode: null,
      },

      tab: 0,
      emailAuthDialog: false,

      resultDialog: false,

      rtMsg: null,
    };
  },
  created() {
    if (this.$store.getters.getAccessToken) this.$router.replace('/');
    this.title = 'Log In to Throw Box';
  },
  watch: {
    tab(val) {
      if (val === 0) {
        this.title = 'Log In to Throw Box';
      } else {
        this.title = 'Sign Up to Throw Box';
      }
    },
  },
  methods: {
    Login() {
      this.$axios
        .post('/signIn/', this.LoginForm)
        .then((r) => {
          localStorage.setItem('accessToken', r.data.AccessToken);
          return this.$axios.get('/userDetail');
        })
        .then((r2) => {
          console.log(r2);
          localStorage.setItem('userName', r2.data.ID);
          this.$store.dispatch('commitGetToken');
          this.$router.replace('/');
        })
        .catch((e) => {
          console.log(e.response);
          this.resultDialog = true;
          this.rtMsg = e.response.data.error;
        });
    },
    SignUp() {
      this.$axios
        .post('/signUp/', this.SignUpForm)
        .then(() => {
          this.emailAuthDialog = true;
          this.emailConfirmData.username = this.SignUpForm.username;
        })
        .catch((e) => {
          console.log(e.response);
          this.resultDialog = true;

          this.rtMsg = e.response.data.error;
        });
    },
    emailAuth() {
      this.$axios
        .post('/signUpConfirm/', this.emailConfirmData)
        .then((r) => {
          console.log(r);
          this.emailAuthDialog = false;
          this.resultDialog = true;
          this.rtMsg = 'You have Successfully signed up ThrowBox!';
        })
        .catch((e) => {
          console.log(e);
          this.resultDialog = true;

          this.rtMsg = e.response.data.error;
        });
    },
    findPassword() {},
    notifyClickOk() {
      this.resultDialog = false;
      if (this.rtMsg === 'You have Successfully signed up ThrowBox!') {
        this.SignUpForm.username = null;
        this.SignUpForm.password = null;
        this.SignUpForm.passwordConfirm = null;
        this.SignUpForm.email = null;
        this.tab = 0;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.signInDivider {
  width: 70px;
  margin: auto;
  background-color: #3f51b5;
  height: 2px;
}
.SignInTitle {
  margin-top: 40px;
  margin-bottom: 30px;
  text-align: center;
  font-size: 30px;
  font-weight: 300;
  letter-spacing: 2px;
}
.dialogTitle {
  color: #343a40;
  text-align: center;
  font-size: 22px;
  font-weight: 300;
  letter-spacing: 2px;
}
.dialogSubTitle {
  color: #5a5a5a;
  text-align: center;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: 2px;
}
</style>
