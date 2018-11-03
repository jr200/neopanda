<template>
  <div class="container">
    <div class="large-12 medium-12 small-12 cell">
      <label>File
        <input type="file" id="file" ref="file" v-on:change="handleFileUpload()"/>
      </label>
        <button v-on:click="submitFile()">Submit</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

  export default {
    data(){
      return {
        file: '',
        text: ''
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
        let formData = new FormData();
        formData.append('file', this.file);
        axios.post( '/single-file',
          formData,
          {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
          }
        ).then(function(){
          console.log('SUCCESS!!');
        })
        .catch(function(){
          console.log('FAILURE!!');
        });
      },
    }
  }
</script>

<style lang="css">
</style>
