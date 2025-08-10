import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import Loader from "../components/Common/Loader";
import List from "../components/Dashboard/List";
import Header from "../components/Common/Header";
import CoinInfo from "../components/Coin/Coininfo";
import LineChart from "../components/Coin/LineChart";
import DropDown from "../components/Coin/DropDown";
import PriceType from "../components/Coin/priceType";
import { getChartData } from "../functions/coinObject";
import Footer from "../components/Common/Footer";
function CoinPage() {
  // Add the style for blue text
  const blueTextStyle = {
    color: "#3a80e9"
  };

  const { id } = useParams();
  const [isLoading, setIsLoading] = useState(true);
  const [isFetching, setIsFetching] = useState(false);
  const [coinData, setCoinData] = useState(null);
  const [lineData, setLineData] = useState(null);
  const [volumeData, setVolumeData] = useState(null);
  const [days, setDays] = useState(30);
  const [newType, setNewType] = useState("prices");
  const hasFetched = useRef(false);

  const formatChartData = (chartData) => {
    if (!chartData) return null;
    
    return {
      labels: chartData.map((item) => {
        const date = new Date(item[0]);
        return date.getDate() + "/" + (date.getMonth() + 1) + "/" + date.getFullYear();
      }),
      datasets: [
        {
          data: chartData.map((item) => item[1]),
          backgroundColor: "rgba(58,128,233,0.1)",
          borderColor: "#3a80e9",
          borderWidth: 2,
          fill: true,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto1",
        },
      ],
    };
  };

  const formatVolumeData = (volumeData) => {
    if (!volumeData) return null;
    
    return {
      labels: volumeData.map((item) => {
        const date = new Date(item[0]);
        return date.getDate() + "/" + (date.getMonth() + 1) + "/" + date.getFullYear();
      }),
      datasets: [
        {
          data: volumeData.map((item) => item[1]),
          backgroundColor: "rgba(58,128,233,0.1)",
          borderColor: "#3a80e9",
          borderWidth: 2,
          fill: true,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto1",
        },
      ],
    };
  };

  const handleDaysChange = (e) => {
    const newDays = e.target.value;
    setDays(newDays);
    setIsLoading(true);

    if (coinData && coinData.chart_data && coinData.chart_data[newDays] && coinData.volume_data && coinData.volume_data[newDays]) {
      const formattedData = formatChartData(coinData.chart_data[newDays]);
      const formattedVolumeData = formatVolumeData(coinData.volume_data[newDays]);
      setLineData(formattedData);
      setVolumeData(formattedVolumeData);
    }
    setIsLoading(false);
  };

  const handlePriceType = (e, newTypeVal) => {
    console.log("Price type changed to:", newTypeVal);
    setNewType(newTypeVal);
  };

  async function getData() {
    if (isFetching) return;
    setIsFetching(true);
    setIsLoading(true);

    try {
      const data = await getChartData(id);
      console.log("Raw data received in Coin.js:", data);
      console.log("Chart data for current days:", data?.chart_data?.[days]);
      console.log("Volume data for current days:", data?.volume_data?.[days]);
      
      if (data) {
        setCoinData(data);
        if (data.chart_data && data.chart_data[days]) {
          const formattedData = formatChartData(data.chart_data[days]);
          console.log("Formatted chart data:", formattedData);
          setLineData(formattedData);
        } else {
          console.log("No chart data available for days:", days);
          console.log("Available chart data periods:", Object.keys(data.chart_data || {}));
        }
        
        if (data.volume_data && data.volume_data[days]) {
          const formattedVolumeData = formatVolumeData(data.volume_data[days]);
          console.log("Formatted volume data:", formattedVolumeData);
          setVolumeData(formattedVolumeData);
        } else {
          console.log("No volume data available for days:", days);
          console.log("Available volume data periods:", Object.keys(data.volume_data || {}));
        }
      }
    } catch (err) {
      console.error("Error fetching chart data:", err);
    } finally {
      setIsFetching(false);
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (!hasFetched.current && id) {
      hasFetched.current = true;
      getData();
    }
  }, [id]);

  return (
    <div>
      <Header />
      {/* Add a style element to force the coin description text color */}
      <style>
        {`
          .coin-info-desc {
            color: #3a80e9 !important;
          }
        `}
      </style>
      
      {isLoading ? (
        <Loader />
      ) : (
        <div className="flex flex-col gap-4">
          <div className="grey-wrapper">
            {coinData && (
              <List
                color="darkgrey"
                coin={{
                  id: coinData.id,
                  name: coinData.name,
                  symbol: coinData.symbol,
                  image: coinData.logo,
                  current_price: coinData.current_price,
                  price_change_percentage_24h: coinData.price_change_percent_24h,
                  total_volume: coinData.volume,
                  market_cap: coinData.market_cap,
                }}
                delay={(1 % 8) * 0.2}
              />
            )}
          </div>

          <div className="grey-wrapper">
            <div className="flex flex-row items-center justify-start gap-2 pl-4 pt-6">
              Price Change In
              <DropDown days={days} handleDaysChange={handleDaysChange} />
            </div>

            <PriceType price={newType} handlePrice={handlePriceType} />
            <LineChart 
              chartData={newType === "prices" ? lineData : volumeData} 
              priceType={newType} 
              multiAxis={false} 
            />
          </div>

          {coinData && (
            <div className="grey-wrapper">
              <div className="p-4">
                <div className="flex items-center gap-3 mb-4">
                  <img 
                    src={coinData.logo} 
                    alt={coinData.name} 
                    className="w-8 h-8" 
                    onError={(e) => {e.target.src = "/assets/default-coin.png"}}
                  />
                  <h3 className="text-xl font-semibold">{coinData.name} ({coinData.symbol})</h3>
                </div>
                <CoinInfo
                  heading={`About ${coinData.name}`}
                  desc={coinData.description || ""}
                  delay={0}
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

export default CoinPage;