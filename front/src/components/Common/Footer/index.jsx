// src/components/Common/Footer/index.jsx
import React from "react";
import { motion } from "framer-motion";
import "./styles.css";

function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <motion.footer 
      className="footer-container"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }} 
    >
      <div className="footer-content">
        <div className="footer-section">
          <h3 className="footer-title">CryptoSpot</h3>
          <p className="footer-description">
            Your trusted platform for crypto trading, exchange and market analysis.
          </p>
          <div className="social-icons">
            <a href="#" className="social-icon">
              <i className="fab fa-twitter"></i>
            </a>
            <a href="#" className="social-icon">
              <i className="fab fa-discord"></i>
            </a>
            <a href="#" className="social-icon">
              <i className="fab fa-telegram"></i>
            </a>
          </div>
        </div>
        
        
        <div className="footer-section">
          <h4 className="footer-subtitle">Support</h4>
          <ul className="footer-links">
            <li><a href="#">Help Center</a></li>
            <li><a href="#">Contact Us</a></li>
            <li><a href="#">Status</a></li>
            <li><a href="#">API Documentation</a></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4 className="footer-subtitle">Company</h4>
          <ul className="footer-links">
            <li><a href="#">About Us</a></li>
            <li><a href="#">Careers</a></li>
            <li><a href="#">Blog</a></li>
            <li><a href="#">Terms of Service</a></li>
            <li><a href="#">Privacy Policy</a></li>
          </ul>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>© {currentYear} CryptoSpot. All rights reserved.</p>
      </div>
    </motion.footer>
  );
}

export default Footer;