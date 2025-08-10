import React, { useState, useEffect } from 'react';
import { authAPI } from '../../functions/auth';
import './styles.css';
import { convertNums } from '../../functions/ConvertNums';
import Loader from '../Common/Loader';

const ProfileComponent = () => {
  const [activeTab, setActiveTab] = useState('myWallet');
  const [profileData, setProfileData] = useState({
    user: {},
    wallets: [],
    totalPortfolioValueUSD: '0',
    transactions: [],
    blockchainTransactions: [],
    exchanges: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        setLoading(true);
        // Fetch profile data which includes user, wallets, and transactions
        const data = await authAPI.fetchFullProfileData();
        setProfileData(data);
        console.log('Fetched profile data:', data);
      } catch (err) {
        console.error('Error fetching profile data:', err);
        setError('Failed to load profile data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  // Get combined transaction history sorted by date (most recent first)
  const getAllTransactions = () => {
    const allTransactions = [
      ...(profileData.transactions || []).map(tx => ({
        date: new Date(tx.created_at),
        displayDate: new Date(tx.created_at).toLocaleDateString(),
        txId: tx.reference_id,
        status: tx.status,
        amount: tx.amount,
        fee: tx.fee,
        type: tx.transaction_type,
        currency: tx.coin,
        currencyIcon: `/assets/coins/${tx.coin.toLowerCase()}.png`,
        source: 'fiat'
      })),
      ...(profileData.blockchain_transactions || []).map(tx => ({
        date: new Date(tx.created_at),
        displayDate: new Date(tx.created_at).toLocaleDateString(),
        txId: tx.tx_hash?.substring(0, 10) || 'pending',
        status: tx.status,
        amount: tx.amount,
        fee: tx.network_fee,
        type: tx.transaction_type,
        currency: tx.coin,
        currencyIcon: `/assets/coins/${tx.coin.toLowerCase()}.png`,
        source: 'blockchain'
      })),
      ...(profileData.exchanges || []).map(ex => ({
        date: new Date(ex.created_at),
        displayDate: new Date(ex.created_at).toLocaleDateString(),
        txId: `EX-${ex.id}`,
        status: 'Completed',
        fromAmount: ex.from_amount,
        toAmount: ex.to_amount,
        fromCurrency: ex.from_coin,
        toCurrency: ex.to_coin,
        fee: ex.fee,
        type: 'EXCHANGE',
        source: 'exchange'
      }))
    ];

    return allTransactions.sort((a, b) => b.date - a.date);
  };
 
  
  return (
    <>
      {loading ? (
        <Loader />
      ) : (
        <div className="wallet-container">
          {/* Balance Section */}
          <div className="balance-section">
            <div className="balance-header">
              <h2>My Balance</h2>
            </div>
            <div className="balance-amount">
              <h1>${parseFloat(profileData.total_portfolio_value_usd || 0).toFixed(2)}</h1>
              <span className="fiat-value">Total Portfolio Value</span>
            </div>
          </div>

          {/* Wallet Balances */}
          <div className="section-title">
            My Wallets
          </div>
          <div className="wallet-balances">
            {profileData.wallets && profileData.wallets.length > 0 ? (
              profileData.wallets.map((wallet, index) => (
                <div className="balance-card" key={index}>
                  <div className="currency-info">
                    <img 
                      src={wallet.logo || `/assets/coins/${wallet.coin.toLowerCase()}.png`} 
                      alt={wallet.coin} 
                      className="currency-icon" 
                      onError={e => {e.target.src = "/assets/default-coin.png"}}
                    />
                    <div className="currency-details">
                      <span className="currency-name">{wallet.coin_name || wallet.coin}</span>
                      <span className="balance-value">{parseFloat(wallet.balance).toFixed(8)} {wallet.coin}</span>
                      <span className="fiat-balance">~ ${parseFloat(wallet.usd_value || 0).toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-wallets">No wallet balances available</div>
            )}
          </div>

          {/* Recent Activity Section */}
          <div className="recent-activity-section">
            <h3 className="section-title">Recent Activity</h3>
            
            {getAllTransactions().length > 0 ? (
              <div className="activity-table">
                <div className="table-header">
                  <div className="header-cell">Date</div>
                  <div className="header-cell">Transaction ID</div>
                  <div className="header-cell">Status</div>
                  <div className="header-cell">Amount</div>
                  <div className="header-cell">Type</div>
                </div>
                
                {getAllTransactions().slice(0, 15).map((tx, index) => (
                  <div className="table-row" key={index}>
                    <div className="table-cell date-cell">{tx.displayDate}</div>
                    
                    <div className="table-cell txid-cell">
                      <span className="tx-hash">{tx.txId}</span>
                    </div>
                    
                    <div className="table-cell status-cell">
                      <span className={`status-badge ${tx.status?.toLowerCase() === 'completed' ? 'completed' : 'pending'}`}>
                        {tx.status || 'Completed'}
                      </span>
                    </div>
                    
                    <div className="table-cell amount-cell">
                      {tx.source === 'exchange' ? (
                        <div className="exchange-amount">
                          {tx.fromAmount} {tx.fromCurrency} →<br />
                          {tx.toAmount} {tx.toCurrency}
                        </div>
                      ) : (
                        <div className="transaction-amount">
                          {tx.type?.includes('DEPOSIT') ? '+' : '-'}{tx.amount} {tx.currency}
                        </div>
                      )}
                    </div>
                    
                    <div className="table-cell type-cell">
                      {tx.type || 'EXCHANGE'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-transactions">No transaction history available</div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ProfileComponent;