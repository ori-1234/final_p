import React from 'react';
import Register from '../components/Register';
import Header from '../components/Common/Header';
import Footer from '../components/Common/Footer';

function RegisterPage() {
  return (
    <>
      <div>
        <Header />
      </div>
      <div>
        <Register />
      </div>
      <Footer />
    </>
  );
}

export default RegisterPage;