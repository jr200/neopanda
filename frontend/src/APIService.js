import axios from 'axios';
const API_URL = 'http://localhost:8000';
export class APIService{

  constructor(){
  }

  getContacts() {
      const url = `${API_URL}/contacts/`;
      return axios.get(url).then(response => response.data);
  }

  getContact(pk) {
      const url = `${API_URL}/contacts/${pk}`;
      return axios.get(url).then(response => response.data);
  }

  createContact(contact){
    const url = `${API_URL}/contacts/`;
    return axios.post(url,contact);
  }

  updateContact(contact){
    const url = `${API_URL}/contacts/${contact.pk}`;
    return axios.put(url,contact);
  }

  deleteContact(contact){
    const url = `${API_URL}/contacts/${contact.pk}`;
    return axios.delete(url);
  }

}
