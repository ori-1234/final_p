import api from './axios';

export const authAPI = {
    login: async (username, password) => {
        try {
            const response = await api.post('user/login/', {
                username,
                password
            });
            
            if (response.data) {
                return {
                    success: true,
                    user: response.data.user
                };
            }
            throw new Error('Login failed');
        } catch (error) {
            console.error('Login error:', error);
            throw new Error(error.response?.data?.error || 'Login failed');
        }
    },

    register: async (userData) => {
        try {
            // Format the data to match backend expectations
            const formattedData = {
                username: userData.username,
                email: userData.email,
                password: userData.password,
                first_name: userData.first_name || '',
                last_name: userData.last_name || '',
                phone_number: userData.phone_number || ''
            };

            const response = await api.post('user/register/', formattedData);
            
            if (response.data && response.data.user) {
                return {
                    success: true,
                    user: response.data.user
                };
            }
            throw new Error(response.data?.message || 'Registration failed');
        } catch (error) {
            console.error('Registration error:', error);
            // Handle validation errors from the backend
            if (error.response?.data) {
                const errors = error.response.data;
                let errorMessage = '';
                
                // Format validation errors
                Object.keys(errors).forEach(key => {
                    const messages = Array.isArray(errors[key]) ? errors[key] : [errors[key]];
                    errorMessage += `${key}: ${messages.join(', ')}\n`;
                });
                
                throw new Error(errorMessage || 'Registration failed');
            }
            throw new Error(error.message || 'Registration failed');
        }
    },

    logout: async () => {
        try {
            await api.post('user/logout/');
            return { success: true };
        } catch (error) {
            console.error('Logout error:', error);
            throw new Error('Logout failed');
        }
    },

    authenticated_user: async () => {
        try {
            await api.get('user/authenticated_user/');
            return { isAuthenticated: true };
        } catch (error) {
            return { isAuthenticated: false };
        }
    },

    fetchFullProfileData: async () => {
        try {
            const response = await api.get('user/profile/');
            return response.data;
        } catch (error) {
            console.error('Fetch profile data error:', error);
            throw new Error('Failed to fetch profile data');
        }
    },

    // Helper functions for specific wallet operations
    getWalletBySymbol: (wallets, symbol) => {
        const wallet = wallets.find(w => w.coin === symbol);
        return {
            balance: wallet ? parseFloat(wallet.balance) : 0,
            isAvailable: !!wallet,
            wallet: wallet || null
        };
    },

    // Helper method to format currency amounts
    formatAmount: (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Helper method to calculate fees
    calculateFee: (amount, feePercentage = 0.03) => {
        const fee = amount * feePercentage;
        return {
            fee: fee,
            netAmount: amount - fee,
            total: amount
        };
    }
};

export const marketAPI = {
    getMarketOverview: async () => {
        try {
            const response = await api.get('analytics/market_overview/');
            return response.data;
        } catch (error) {
            console.error('Error fetching market overview:', error);
            throw error;
        }
    },

    getCoinDetails: async (symbol) => {
        try {
            const response = await api.get(`analytics/coin_details/${symbol}/`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching coin details for ${symbol}:`, error);
            throw error;
        }
    },

    getComparison: async (crypto1, crypto2, days = 30) => {
        try {
            const response = await api.get('analytics/compare_coins/', {
                params: { crypto1, crypto2, days }
            });
            return response.data;
        } catch (error) {
            console.error(`Error comparing ${crypto1} and ${crypto2}:`, error);
            throw error;
        }
    },

    getCoins: async () => {
        const response = await api.get('exchange/coins/');
        return response.data;
    }
};

export const analysisAPI = {
    getAnalysisResult: async (symbol) => {
        try {
            const response = await api.get(`analysis/get-analysis-result/${symbol}/`);
            
            if (response.status === 200 && response.data.status === 'success') {
                // We now return the nested 'data' object directly
                return response.data.data;
            } else if (response.status === 204 || (response.data && response.data.status === 'no-data')) {
                return null; // No new data available
            }
            throw new Error('Failed to fetch analysis results with status: ' + response.status);
        } catch (error) {
            console.error(`Error fetching analysis result for ${symbol}:`, error.message);
            return null;
        }
    }, 
}; 