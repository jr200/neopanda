import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import Contacts from '@/components/Contacts'
import TestComp from '@/components/TestComp'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: HelloWorld
    },
    {
      path: '/Contacts',
      name: 'Contacts',
      component: Contacts
    },
    {
      path: '/TestComp',
      name: 'TestComp',
      component: TestComp
    }
  ]
})
