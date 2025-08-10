import React from 'react';
import Login from '../components/Login';
import Header from '../components/Common/Header';
import Footer from '../components/Common/Footer';

function LoginPage() {
  return (
    <>
      <div>
        <Header />
      </div>
      <div>
      <Login />
    </div>
    <Footer />
    </>
  );
}

export default LoginPage;