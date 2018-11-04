<template lang="html">
  <div>
  <div class="reg_fields">
    <v-text-field
      label="First Name"
      outline
      required
      v-model="firstName">
    </v-text-field>
    <v-text-field
      label="Last Name"
      outline
      required
      v-model="lastName">
    </v-text-field>
    <v-text-field
      label="Email"
      outline
      required
      v-model="email">
    </v-text-field>
  </div>
    <div class="submit">
      <v-btn v-on:click="submit" outline>SUBMIT</v-btn>
       <a v-if="downloadReady" :href="textFile" download="info.txt" id="downloadlink">Download</a>
    </div>
  </div>

</template>

<script>
export default {
  data(){
    return {
      firstName: '',
      lastName: '',
      email: '',
      textFile: '',
      downloadReady: false
    }
  },
  methods: {
    submit: function () {
      console.log("submitted!")
      var data = new Blob([this.createText()], {type: 'text/plain'});
      if (this.textFile !== '') {
        window.URL.revokeObjectURL(textFile);
      }
      this.textFile = window.URL.createObjectURL(data);
      this.downloadReady = true;
    },
    createText: function () {
      let text = "First Name: " + this.firstName + '\n'
        + "Last Name: " +  this.lastName + '\n'
        + "Email: " + this.email
      return text
    }
  }
}
</script>

<style scoped>
  .reg_fields {
    padding: 100px;
  }
  .submit {
    margin-left: 100px;
  }
</style>
