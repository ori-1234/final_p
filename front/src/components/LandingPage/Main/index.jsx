// src/components/LandingPage/index.jsx
import React, { useEffect } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useInView } from 'react-intersection-observer';
import Button from '../../Common/Button';
import { FaChartLine, FaExchangeAlt, FaShieldAlt, FaGlobe, FaUsers, FaMobileAlt, FaRobot, FaPercentage, FaChartBar, FaHandshake } from 'react-icons/fa';
import './styles.css';

// Animation variants for sections
const sectionVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6, when: "beforeChildren", staggerChildren: 0.2 }
  }
};

// Component for scroll-triggered animations
const AnimatedSection = ({ children, className }) => {
  const controls = useAnimation();
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  useEffect(() => {
    if (inView) {
      controls.start('visible');
    }
  }, [controls, inView]);

  return (
    <motion.section
      ref={ref}
      className={className}
      variants={sectionVariants}
      initial="hidden"
      animate={controls}
    >
      {children}
    </motion.section>
  );
};

function LandingPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <motion.h1 
                className="font-bold text-white text-9xl m-0"
                initial={{opacity: 0, y: 50}} 
                animate={{opacity: 1, y: 0}} 
                transition={{duration: 0.5}}
              >
                AI-Driven
              </motion.h1>
              <motion.h1 
                className="text-blue text-9xl m-0 font-bold"
                initial={{opacity: 0, y: 50}} 
                animate={{opacity: 1, y: 0}} 
                transition={{duration: 0.5, delay: 0.5}}
              >
                Predictions.
              </motion.h1>
              <motion.p 
                className="text-xl text-grey mt-8"
                initial={{opacity: 0, y: 50}} 
                animate={{opacity: 1, y: 0}} 
                transition={{duration: 0.5, delay: 1}}
              >
                Your premier crypto analysis platform. Gain an edge with our advanced AI, providing predictive insights to maximize your investment potential.
              </motion.p>

              <motion.div 
                className="flex gap-6 items-center justify-start mt-6"
                initial={{opacity: 0, x: 50}} 
                animate={{opacity: 1, x: 0}} 
                transition={{duration: 0.5, delay: 1.5}}
              >
                <Link to="/Dashboard"><Button label={'Dashboard'} /></Link>
                <Link to="/Register"><Button outLined={true} label={'Get Started'}/></Link>
              </motion.div>
            </div>
            
            <motion.div 
              className="hero-image"
              initial={{opacity: 0, scale: 0.8}} 
              animate={{opacity: 1, scale: 1}} 
              transition={{duration: 0.8, delay: 0.5}}
            >
              <img 
                src="https://images.unsplash.com/photo-1621761191319-c6fb62004040?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                alt="Crypto analysis visualization" 
                className="rounded-lg shadow-custom-blue"
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Analysis Platform Highlight Section */}
      <AnimatedSection className="broker-section">
        <div className="container">
          <motion.h2 
            className="section-title"
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
          >
            The <span className="text-blue">Smart Platform</span> For Smart Investors
          </motion.h2>
          
          <div className="broker-content">
            <motion.div 
              className="broker-text"
              variants={{
                hidden: { opacity: 0, x: -30 },
                visible: { opacity: 1, x: 0 }
              }}
            >
              <h3>Comprehensive Crypto Analysis</h3>
              <p>We provide a complete analysis solution, handling all aspects of cryptocurrency market research on your behalf. From sentiment analysis to predictive modeling, our platform simplifies the complexities of crypto investing.</p>
              <p>Unlike traditional signal providers, our platform provides in-depth, data-driven analysis with a focus on predictive accuracy.</p>
              
              <div className="broker-benefits">
                <div className="benefit-item">
                  <FaRobot className="benefit-icon" />
                  <div>
                    <h4>AI-Powered Predictions</h4>
                    <p>We use advanced machine learning to predict market movements and identify opportunities.</p>
                  </div>
                </div>
                
                <div className="benefit-item">
                  <FaChartBar className="benefit-icon" />
                  <div>
                    <h4>In-Depth Analysis</h4>
                    <p>Access detailed reports covering sentiment, technicals, and on-chain data for a holistic market view.</p>
                  </div>
                </div>
              </div>
            </motion.div>
            
            <motion.div 
              className="broker-image"
              variants={{
                hidden: { opacity: 0, x: 30 },
                visible: { opacity: 1, x: 0 }
              }}
            >
              <img 
                src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                alt="Analysis dashboard" 
                className="rounded-lg shadow-custom-blue"
              />
            </motion.div>
          </div>
        </div>
      </AnimatedSection>

      {/* Subscription Plans Section */}
      <AnimatedSection className="fees-section">
        <div className="container">
          <motion.h2 
            className="section-title"
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
          >
            Flexible <span className="text-blue">Subscription Plans</span>
          </motion.h2>
          
          <motion.div 
            className="fee-cards"
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
          >
            <div className="fee-card">
              <div className="fee-card-header">
                <h3>Basic</h3>
              </div>
              <div className="fee-rate">Free</div>
              <ul className="fee-features">
                <li>Basic market overview</li>
                <li>Limited to 3 coin analyses per day</li>
                <li>Standard customer support</li>
                <li>Basic portfolio analytics</li>
              </ul>
            </div>
            
            <div className="fee-card highlight">
              <div className="popular-tag">Most Popular</div>
              <div className="fee-card-header">
                <h3>Advanced</h3>
              </div>
              <div className="fee-rate">$29/mo</div>
              <ul className="fee-features">
                <li>Unlimited AI market analysis</li>
                <li>Full access to predictive models</li>
                <li>Priority customer support</li>
                <li>Advanced sentiment analysis tools</li>
                <li>Real-time market alerts</li>
              </ul>
            </div>
            
            <div className="fee-card">
              <div className="fee-card-header">
                <h3>Institutional</h3>
              </div>
              <div className="fee-rate">Contact Us</div>
              <ul className="fee-features">
                <li>Tailored analysis solutions</li>
                <li>Dedicated data scientist</li>
                <li>24/7 priority support</li>
                <li>Custom API integration</li>
                <li>Bespoke AI models</li>
              </ul>
            </div>
          </motion.div>
          
          <motion.div 
            className="fee-note"
            variants={{
              hidden: { opacity: 0 },
              visible: { opacity: 1 }
            }}
          >
            <p>All plans come with a 7-day free trial. Unlock the full potential of our AI with the Advanced plan.</p>
          </motion.div>
        </div>
      </AnimatedSection>

      {/* AI Analysis Section */}
      <AnimatedSection className="ai-section">
        <div className="container">
          <motion.h2 
            className="section-title"
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
          >
            <span className="text-blue">AI-Powered</span> Market Intelligence
          </motion.h2>
          
          <div className="ai-content">
            <motion.div 
              className="ai-image"
              variants={{
                hidden: { opacity: 0, x: -30 },
                visible: { opacity: 1, x: 0 }
              }}
            >
              <img 
                src="https://images.unsplash.com/photo-1639762681057-408e52192e55?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                alt="AI analysis visualization" 
                className="rounded-lg shadow-custom-blue"
              />
            </motion.div>
            
            <motion.div 
              className="ai-text"
              variants={{
                hidden: { opacity: 0, x: 30 },
                visible: { opacity: 1, x: 0 }
              }}
            >
              <h3>Advanced Analysis Tools at Your Fingertips</h3>
              <p>Our platform leverages cutting-edge AI and machine learning algorithms to provide you with predictive market insights that traditional analysis can't match.</p>
              
              <div className="ai-features">
                <div className="ai-feature">
                  <FaRobot className="ai-icon" />
                  <div>
                    <h4>Sentiment Analysis</h4>
                    <p>Our AI continuously scans social media, news outlets, and forums to gauge market sentiment and predict price movements before they happen.</p>
                  </div>
                </div>
                
                <div className="ai-feature">
                  <FaChartBar className="ai-icon" />
                  <div>
                    <h4>Pattern Recognition</h4>
                    <p>Advanced machine learning algorithms identify trading patterns and market anomalies that human traders might miss.</p>
                  </div>
                </div>
                
                <div className="ai-feature">
                  <FaChartLine className="ai-icon" />
                  <div>
                    <h4>Predictive Analytics</h4>
                    <p>Get AI-generated price forecasts based on historical data, current market conditions, and sentiment analysis.</p>
                  </div>
                </div>
              </div>
              
              <Link to="/">
                <Button label={'Explore Analysis'} />
              </Link>
            </motion.div>
          </div>
        </div>
      </AnimatedSection>

      {/* Features Section */}
      <AnimatedSection className="features-section">
        <div className="container">
          <motion.h2 
            className="section-title"
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
          >
            Our <span className="text-blue">Features</span>
          </motion.h2>
          
          <div className="features-grid">
            <motion.div 
              className="feature-card"
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <div className="feature-icon">
                <FaRobot />
              </div>
              <h3>AI-Powered Predictions</h3>
              <p>Leverage our machine learning models to get predictive insights on market trends and price movements.</p>
            </motion.div>

            <motion.div 
              className="feature-card"
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <div className="feature-icon">
                <FaChartBar />
              </div>
              <h3>Comprehensive Analysis</h3>
              <p>Get a holistic view of the market with our in-depth technical and sentiment analysis reports.</p>
            </motion.div>

            <motion.div 
              className="feature-card"
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <div className="feature-icon">
                <FaShieldAlt />
              </div>
              <h3>Reliable & Secure</h3>
              <p>Your data is protected with our state-of-the-art security infrastructure and protocols.</p>
            </motion.div>

            <motion.div 
              className="feature-card"
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <div className="feature-icon">
                <FaGlobe />
              </div>
              <h3>Global Market Coverage</h3>
              <p>Access analysis for a wide range of cryptocurrencies from across the globe.</p>
            </motion.div>

            <motion.div 
              className="feature-card"
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <div className="feature-icon">
                <FaMobileAlt />
              </div>
              <h3>Mobile Ready</h3>
              <p>Take our crypto analysis on the go with our responsive mobile interface.</p>
            </motion.div>

            <motion.div 
              className="feature-card"
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <div className="feature-icon">
                <FaUsers />
              </div>
              <h3>Community Insights</h3>
              <p>Join our growing community of investors to share insights and strategies.</p>
            </motion.div>
          </div>
        </div>
      </AnimatedSection>

      {/* Products Section */}
      <AnimatedSection className="products-section">
        <div className="container">
          <motion.h2 
            className="section-title"
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
          >
            Our <span className="text-blue">Products</span>
          </motion.h2>

          <div className="products-wrapper">
            <motion.div 
              className="product-card"
              variants={{
                hidden: { opacity: 0, x: -50 },
                visible: { opacity: 1, x: 0 }
              }}
            >
              <div className="product-content">
                <h3>Analysis Dashboard</h3>
                <p>Our comprehensive dashboard provides detailed insights into market trends, price movements, and portfolio performance, all in one place.</p>
                <Link to="/Dashboard">
                  <Button label={'Explore Dashboard'} />
                </Link>
              </div>
              <div className="product-image">
                <img 
                  src="https://images.unsplash.com/photo-1642104704074-907c0698cbd9?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                  alt="Crypto Dashboard" 
                  className="rounded-lg"
                />
              </div>
            </motion.div>

            <motion.div 
              className="product-card reverse"
              variants={{
                hidden: { opacity: 0, x: 50 },
                visible: { opacity: 1, x: 0 }
              }}
            >
              <div className="product-image">
                <img 
                  src="https://images.unsplash.com/photo-1518186285589-2f7649de83e0?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                  alt="AI Predictions" 
                  className="rounded-lg"
                />
              </div>
              <div className="product-content">
                <h3>AI Prediction Engine</h3>
                <p>Our secure and intuitive prediction engine allows you to get AI-powered insights with maximum efficiency.</p>
                <Link to="/analysis">
                  <Button label={'Get Predictions'} />
                </Link>
              </div>
            </motion.div>

            <motion.div 
              className="product-card"
              variants={{
                hidden: { opacity: 0, x: -50 },
                visible: { opacity: 1, x: 0 }
              }}
            >
              <div className="product-content">
                <h3>Comparison Tool</h3>
                <p>Compare different cryptocurrencies side by side, analyzing historical data and performance metrics to make informed investment decisions.</p>
                <Link to="/compare">
                  <Button label={'Compare Coins'} />
                </Link>
              </div>
              <div className="product-image">
                <img 
                  src="https://images.unsplash.com/photo-1605792657660-596af9009e82?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                  alt="Comparison Tool" 
                  className="rounded-lg"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </AnimatedSection>

      {/* About Section */}
      <AnimatedSection className="about-section">
        <div className="container">
          <div className="about-wrapper">
            <motion.div 
              className="about-content"
              variants={{
                hidden: { opacity: 0, y: 50 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <h2 className="section-title">About <span className="text-blue">Us</span></h2>
              <p>We are a team of passionate crypto enthusiasts, financial technology experts, and data scientists committed to making cryptocurrency analysis accessible and profitable for everyone.</p>
              <p>Founded in 2024, CryptoSpot has quickly grown to become a trusted analysis platform for thousands of users worldwide, providing cutting-edge tools and AI-powered insights for the crypto market.</p>
              <p>Our mission is to demystify cryptocurrency investments and empower our users with the knowledge and tools they need to succeed in this exciting digital frontier.</p>
            </motion.div>
            
            <motion.div 
              className="about-stats"
              variants={{
                hidden: { opacity: 0, scale: 0.9 },
                visible: { opacity: 1, scale: 1 }
              }}
            >
              <div className="stat-item">
                <span className="stat-number">50K+</span>
                <span className="stat-label">Active Users</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">100+</span>
                <span className="stat-label">Cryptocurrencies</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">1M+</span>
                <span className="stat-label">Predictions Made</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">24/7</span>
                <span className="stat-label">Support</span>
              </div>
            </motion.div>
          </div>
        </div>
      </AnimatedSection>

      {/* CTA Section */}
      <AnimatedSection className="cta-section">
        <div className="container">
          <motion.div 
            className="cta-wrapper"
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: { opacity: 1, y: 0 }
            }}
          >
            <h2>Ready to unlock AI-powered insights?</h2>
            <p>Join thousands of users who are already using our AI-powered analysis platform.</p>
            <div className="cta-buttons">
              <Link to="/Register"><Button label={'Create Account'} /></Link>
              <Link to="/Dashboard"><Button outLined={true} label={'Try Dashboard'} /></Link>
            </div>
          </motion.div>
        </div>
      </AnimatedSection>
    </>
  );
}

export default LandingPage;