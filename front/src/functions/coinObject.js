import { marketAPI } from './auth';
import axios from 'axios';

/**
 * Takes chart data and produces the final chart config object with `labels` + `datasets`.
 */
export async function buildChartData(data1, data2 = null, timeframe = '30') {
  // Extract the correct timeframe data
  const prices1 = data1.chart_data[timeframe] || [];
  const prices2 = data2?.chart_data[timeframe] || null;

  // If we have a second set of prices, produce a two-line chart
  if (prices2) {
    return {
      labels: prices1.map((price) => convertDate(price[0])),
      datasets: [
        {
          label: data1.symbol,
          data: prices1.map((price) => price[1]),
          borderColor: "#3a80e9",
          borderWidth: 2,
          fill: false,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto1",
        },
        {
          label: data2.symbol,
          data: prices2.map((price) => price[1]),
          borderColor: "#61c96f",
          borderWidth: 2,
          fill: false,
          tension: 0.25,
          pointRadius: 0,
          yAxisID: "crypto2",
        },
      ],
    };
  }

  // Otherwise, just one line
  return {
    labels: prices1.map((price) => convertDate(price[0])),
    datasets: [
      {
        label: data1.symbol,
        data: prices1.map((price) => price[1]),
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
}

/**
 * Fetches coin data using the marketAPI from auth.js
 */
export async function getChartData(symbol) {
  try {
    console.log("Fetching data for symbol:", symbol);
    const data = await marketAPI.getCoinDetails(symbol.toUpperCase());
    console.log("Full API response:", data);
    
    // Ensure we have the expected data structure
    if (!data.chart_data) {
      console.error("No chart_data in response:", data);
      return null;
    }

    return {
      id: data.id,
      name: data.name,
      symbol: data.symbol,
      logo: data.logo,
      description: data.description,
      current_price: data.current_price,
      price_change_percent_24h: data.price_change_percent_24h,
      volume: data.volume,
      market_cap: data.market_cap,
      chart_data: {
        "7": data.chart_data["7"] || [],
        "30": data.chart_data["30"] || [],
        "60": data.chart_data["60"] || [],
        "90": data.chart_data["90"] || [],
        "120": data.chart_data["120"] || [],
        "365": data.chart_data["365"] || [],
      },
      volume_data: {
        "7": data.volume_data && data.volume_data["7"] ? data.volume_data["7"] : [],
        "30": data.volume_data && data.volume_data["30"] ? data.volume_data["30"] : [],
        "60": data.volume_data && data.volume_data["60"] ? data.volume_data["60"] : [],
        "90": data.volume_data && data.volume_data["90"] ? data.volume_data["90"] : [],
        "120": data.volume_data && data.volume_data["120"] ? data.volume_data["120"] : [],
        "365": data.volume_data && data.volume_data["365"] ? data.volume_data["365"] : [],
      }
    };
  } catch (error) {
    console.error("Error fetching chart data:", error);
    return null;
  }
}

/**
 * Helper function to convert timestamp to date string with zero-padding
 */
function convertDate(timestampMs) {
  const myDate = new Date(timestampMs);
  const day = String(myDate.getDate()).padStart(2, '0');
  const month = String(myDate.getMonth() + 1).padStart(2, '0');
  return `${day}/${month}/${myDate.getFullYear()}`;
}

/**
 * Converts API response data into the required coin object format
 */
export const coinObject = (data, setState) => {
  setState({
    id: data.id,
    name: data.name,
    symbol: data.symbol,
    image: data.logo || "",
    desc: data.description || "",
    price_change_percentage_24h: data.price_change_percent_24h || 0,
    total_volume: data.volume || 0,
    current_price: data.current_price || 0,
    last_updated: data.last_updated || "",
    chart_data: data.chart_data || {},
    volume_data: data.volume_data || {},
  });
};