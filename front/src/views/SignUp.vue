<template>
  <v-sheet style="margin-top: 100px">
    <v-card elevation="0" class="pa-4 mx-12" outlined>
      <h1>
        <font color="#03A9F4">Sign Up</font>
      </h1>
      <p></p>
      <br />
      <v-text-field
        label="이메일"
        :rules="rules2"
        hide-details="auto"
        v-model="email"
        hint="ex) 123123@gmail.com"
        persistent-hint
        clearable
        outlined
      ></v-text-field>
      <v-text-field
        append-icon="mdi-account-check-outline"
        color="#673AB7"
        label="아이디"
        v-model="userId"
        hint="중복된 ID 입니다"
        clearable
        outlined
      ></v-text-field>
      <v-text-field color="#03A9F4" label="이름" v-model="name" clearable outlined></v-text-field>
      <v-text-field
        color="#00BCD4"
        label="비밀번호"
        :rules="rules"
        hide-details="auto"
        type="password"
        v-model="password"
        hint="숫자, 영문, 특수기호를 적어도 하나씩은 포함하십시오."
        persistent-hint
        clearable
        outlined
      ></v-text-field>
      <v-text-field
        label="비밀번호 확인"
        :rules="rules"
        hide-details="auto"
        v-model="src"
        clearable
        outlined
      ></v-text-field>
      <br />
      <v-btn class="ma-2" tile color="indigo" dark>
        회원 가입
        <v-icon color="blue" size="30">mdi-account-plus</v-icon>
      </v-btn>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <span v-on="on">ID 중복확인을 했는지 확인하십시오.</span>
        </template>
        <span>경고문구</span>
      </v-tooltip>
    </v-card>
  </v-sheet>
</template>
<script>
export default {
  data: () => ({
    rules: [
      (value) => !!value || 'Required(필수 항목입니다).',
      (value) => (value && value.length >= 8) || '적어도 8자 이상이어야 합니다.',
    ],
    rules2: [(value) => !!value || 'Required(필수 항목입니다).'],
  }),
};
/* export default {
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
}; */
</script>
