<template>
  <div class="container">
    <div class="large-12 medium-12 small-12 cell">
      <label>
        File
        <input type="file" id="file" ref="file" v-on:change="handleFileUpload()"/>
      </label>
        <v-btn v-on:click="submitFile()">Submit</v-btn>
    </div>
    <div class="user_id">
      <v-text-field
        label="User Id"
        outline
        required
        v-model="userId">
      </v-text-field>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

  export default {
    data(){
      return {
        file: '',
        text: '',
        userId: ''
      }
    },
    methods: {
      handleFileUpload(){
        this.file = this.$refs.file.files[0];
        this.readFile();
      },
      readFile: function() {
        let file = this.file;
        if (file) {
          new Promise(function(resolve, reject) {
            var reader = new FileReader();
            reader.onload = function (evt) {
              resolve(evt.target.result);
            };
            reader.readAsText(file);
            reader.onerror = reject;
          })
          .then(this.processFileContent)
          .catch(function(err) {
            console.log(err)
          });
        }
      },
      processFileContent(data){
        this.text = data;
        console.log(data);
      },
      submitData(){
      },
      submitFile(){
        const api = axios.create({baseURL: 'http://localhost:80'})
        api.post('/temp', {
            document: this.text,
            userId: this.userId
        }).then((response) => {
               console.log(response);
        });
        // const body = {
        //   name: "DuckDuckGo",
        //   version: "1.1"
        // }
        // console.log("Sending POST with body", body);
        // let uri = 'http://localhost:80/temp';
        //     axios.post(uri, body).then((response) => {
        //        console.log(response);
        //     });
      },
    }
  }
</script>

<style scoped>
  .user_id {
    margin-top: 20px;
    width: 20%;
  }
</style>
