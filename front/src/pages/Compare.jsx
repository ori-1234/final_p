import React, { useState, useEffect } from 'react';
import Header from '../components/Common/Header';
import SelectCoin from '../components/Compare/SelectCoin';
import DropDown from '../components/Coin/DropDown';
import List from '../components/Dashboard/List';
import CoinInfo from '../components/Coin/Coininfo';
import LineChart from '../components/Coin/LineChart';
import PriceType from '../components/Coin/priceType';
import Loader from '../components/Common/Loader';
import { marketAPI } from '../functions/auth';
import Footer from '../components/Common/Footer';

function ComparePage() {
  // State for the complete data response from the backend.
  const [allCoinData, setAllCoinData] = useState(null);
  // List of coin symbols available (e.g., ["BTC", "ETH", "SOL", ...])
  const [availableCoins, setAvailableCoins] = useState([]);
  
  // Selected coins for comparison.
  const [crypto1, setCrypto1] = useState('BTC');
  const [crypto2, setCrypto2] = useState('ETH');
  
  // Selected coin data (derived from allCoinData).
  const [crypto1Data, setCrypto1Data] = useState(null);
  const [crypto2Data, setCrypto2Data] = useState(null);
  
  // Other UI state.
  const [isLoading, setIsLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [newType, setNewType] = useState('prices');
  const [lineData, setLineData] = useState(null);
  const [volumeData, setVolumeData] = useState(null);

  // Fetch all coin comparison data once when component mounts.
  useEffect(() => {
    const fetchComparisonData = async () => {
      setIsLoading(true);
      try {
        // Call getComparison without parameters so that the backend returns all coins' data.
        const response = await marketAPI.getComparison();
        // Expected format: { data: { BTC: { ... }, ETH: { ... }, ... } }
        if (response.data) {
          setAllCoinData(response.data);
          setAvailableCoins(Object.keys(response.data));
        }
      } catch (error) {
        console.error("Error fetching comparison data:", error);
      }
      setIsLoading(false);
    };

    fetchComparisonData();
  }, []);

  // Update selected coin data and chart data when crypto1, crypto2, days, or allCoinData changes.
  useEffect(() => {
    if (!allCoinData) return;
    
    const coin1Data = allCoinData[crypto1];
    const coin2Data = allCoinData[crypto2];
    setCrypto1Data(coin1Data);
    setCrypto2Data(coin2Data);

    // Each coin's cached chart_data is an object with keys for each timeframe.
    // We extract the selected timeframe (as a string).
    const timeframeKey = String(days);
    
    // Process price data
    const chartData1 = coin1Data && coin1Data.chart_data ? coin1Data.chart_data[timeframeKey] || [] : [];
    const chartData2 = coin2Data && coin2Data.chart_data ? coin2Data.chart_data[timeframeKey] || [] : [];

    // Assume both coins share similar date labels.
    const labels = chartData1.map(item => new Date(item[0]).toLocaleDateString());
    
    setLineData({
      labels,
      datasets: [
        {
          label: coin1Data ? coin1Data.name : '',
          data: chartData1.map(item => item[1]),
          borderColor: "#3a80e9",
          borderWidth: 2,
          fill: false,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto1",
        },
        {
          label: coin2Data ? coin2Data.name : '',
          data: chartData2.map(item => item[1]),
          borderColor: "#61c96f",
          borderWidth: 2,
          fill: false,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto2",
        },
      ],
    });
    
    // Process volume data
    const volumeData1 = coin1Data && coin1Data.volume_data ? coin1Data.volume_data[timeframeKey] || [] : [];
    const volumeData2 = coin2Data && coin2Data.volume_data ? coin2Data.volume_data[timeframeKey] || [] : [];
    
    setVolumeData({
      labels,
      datasets: [
        {
          label: coin1Data ? coin1Data.name : '',
          data: volumeData1.map(item => item[1]),
          borderColor: "#3a80e9",
          borderWidth: 2,
          fill: false,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto1",
        },
        {
          label: coin2Data ? coin2Data.name : '',
          data: volumeData2.map(item => item[1]),
          borderColor: "#61c96f",
          borderWidth: 2,
          fill: false,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto2",
        },
      ],
    });
    
  }, [crypto1, crypto2, days, allCoinData]);

  // Change selection handlers – ensure the user cannot pick the same coin twice.
  const handleCoinChange = (event, isCoin1) => {
    const newValue = event.target.value;
    if (isCoin1) {
      if (newValue !== crypto2) {
        setCrypto1(newValue);
      }
    } else {
      if (newValue !== crypto1) {
        setCrypto2(newValue);
      }
    }
  };

  const handleDaysChange = (event) => {
    setDays(Number(event.target.value));
  };

  const handlePriceType = (e, newTypeVal) => {
    console.log("Price type changed to:", newTypeVal);
    setNewType(newTypeVal);
  };

  return (
    <div>
      <Header />
      {isLoading ? (
        <Loader />
      ) : (
        <div className="flex flex-col gap-4 p-4 min-h-screen">
          {crypto1Data && (
            <div className="grey-wrapper">
              <List
                coin={{
                  id: crypto1Data.id,
                  name: crypto1Data.name,
                  symbol: crypto1Data.symbol,
                  image: crypto1Data.logo,
                  current_price: crypto1Data.current_price,
                  price_change_percentage_24h: crypto1Data.price_change_percent_24h,
                  total_volume: crypto1Data.volume,
                  market_cap: crypto1Data.market_cap,
                }}
                delay={0.2}
                color={"darkgrey"}
              />
            </div>
          )}

          {crypto2Data && (
            <div className="grey-wrapper">
              <List
                coin={{
                  id: crypto2Data.id,
                  name: crypto2Data.name,
                  symbol: crypto2Data.symbol,
                  image: crypto2Data.logo,
                  current_price: crypto2Data.current_price,
                  price_change_percentage_24h: crypto2Data.price_change_percent_24h,
                  total_volume: crypto2Data.volume,
                  market_cap: crypto2Data.market_cap,
                }}
                delay={0.2}
                color={"darkgrey"}
              />
            </div>
          )}

          <div className="grey-wrapper">
          <div className="flex justify-start gap-8 items-center bg-darkgrey">
            <SelectCoin
              crypto1={crypto1}
              crypto2={crypto2}
              handleCoinChange={handleCoinChange}
              availableCoins={availableCoins}
            />
            <DropDown days={days} handleDaysChange={handleDaysChange} />
          </div>
            <PriceType price={newType} handlePrice={handlePriceType} />
            {(lineData && volumeData) ? (
              <LineChart 
                chartData={newType === "prices" ? lineData : volumeData} 
                priceType={newType} 
                multiAxis={true} 
              />
            ) : (
              <div className="flex justify-center items-center h-[400px]">
                Select two coins to compare
              </div>
            )}
          </div>
          
          {/* Coin Descriptions Section */}
            {crypto1Data && (
              <div className="grey-wrapper flex-1">
                <div className="p-4">
                  <div className="flex items-center gap-3 mb-4">
                    <img 
                      src={crypto1Data.logo} 
                      alt={crypto1Data.name} 
                      className="w-8 h-8" 
                      onError={(e) => {e.target.src = "/assets/default-coin.png"}}
                    />
                    <h3 className="text-xl font-semibold">{crypto1Data.name} ({crypto1Data.symbol})</h3>
                  </div>
                  <CoinInfo
                    heading={`About ${crypto1Data.name}`}
                    desc={crypto1Data.description || `No description available for ${crypto1Data.name}.`}
                    delay={0.2}
                    descriptionClass="text-[#3a80e9]" 
                  />
                </div>
              </div>
            )}

            {crypto2Data && (
              <div className="grey-wrapper flex-1">
                <div className="p-4">
                  <div className="flex items-center gap-3 mb-4">
                    <img 
                      src={crypto2Data.logo} 
                      alt={crypto2Data.name} 
                      className="w-8 h-8" 
                      onError={(e) => {e.target.src = "/assets/default-coin.png"}}
                    />
                    <h3 className="text-xl font-semibold">{crypto2Data.name} ({crypto2Data.symbol})</h3>
                  </div>
                  <CoinInfo
                    heading={`About ${crypto2Data.name}`}
                    desc={crypto2Data.description || `No description available for ${crypto2Data.name}.`}
                    delay={0.2}
                    className="text-blue"
                  />
                </div>
              </div>
            )}
        </div>
      )}
      <Footer />
    </div>
  );
}

export default ComparePage;
