<template>
  <nav>
    <v-sheet style="margin-top: 100px">
      <v-card elevation="0" class="pa-4 mx-12" outlined>
        <!-- eslint-disable max-len -->
        <img
          src="data:image/jpeg;base64,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"
          alt="ThrowBox 로고"
          title="ThrowBox 로고"
        />
        <h1>ThrowBox 로그인</h1>
        <br />
        <v-row justify="center">
          <v-col cols="12" sm="6">
            <v-text-field label="이메일" placeholder="E-Mail" v-model="email" clearable filled></v-text-field>
            <v-text-field label="비밀번호" type="password" v-model="password" clearable filled></v-text-field>
          </v-col>
        </v-row>

        <v-btn class="ma-2" width="560" tile color="indigo" dark>
          로그인
          <v-icon color="blue" size="30">mdi-account-key</v-icon>
        </v-btn>
        <p></p>
        <v-btn class="ma-2" width="560" tile color="#00BCD4" dark>
          회원가입
          <v-icon color="blue" size="30">mdi-account-plus</v-icon>
        </v-btn>
      </v-card>
    </v-sheet>
  </nav>
</template>

<style scoped>
nav {
  text-align: center;
}
</style>


<script>
export default {
  data() {
    return {
      userId: null,
      password: null,
      name: null,
      address: null,
      src: null,
    };
  },
  methods: {},
};
</script>
