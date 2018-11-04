<template>
  <div class="container">
    <div class="file_upload">
      <label>
        File
        <input type="file" id="file" ref="file" v-on:change="handleFileUpload()"/>
      </label>
    </div>
    <!-- <div class="user_id">
      <v-text-field
        label="User Id"
        outline
        required
        v-model="userId">
      </v-text-field>
    </div> -->
    <div class="submit">
      <v-btn v-on:click="submitFile()">Submit</v-btn>
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
      },
    }
  }
</script>

<style scoped>
  .file_upload {
    margin-top: 50px;
    margin-left: 50px;
  }
  .submit {
    margin-top: 50px;
    margin-left: 50px;
  }
</style>
