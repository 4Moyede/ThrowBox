<template>
  <v-sheet style="margin-top: 100px">
    <v-card elevation="0" class="pa-4 mx-12" outlined>
      <v-text-field append-icon="mdi-magnify" label="아이디" v-model="userId"></v-text-field>
      <v-text-field label="비밀번호" type="password" v-model="password"></v-text-field>
      <v-text-field label="이름" v-model="name"></v-text-field>
      <v-text-field label="주소" v-model="address"></v-text-field>
      <v-text-field label="이미지" v-model="src"></v-text-field>
      <v-btn>
        <v-icon>mdi-access-point-network</v-icon>
        회원가입
        </v-btn>
      <v-icon color="blue" size="30">mdi-access-point-network</v-icon>
    </v-card>
  </v-sheet>
</template>
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
  methods: {

  },
};
</script>
