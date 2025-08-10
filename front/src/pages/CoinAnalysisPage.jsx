import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Bar, Line } from "react-chartjs-2";
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, TimeScale, Filler } from "chart.js";
import 'chartjs-adapter-date-fns';
import { FaChartBar, FaNewspaper, FaBrain, FaBullseye, FaExclamationTriangle, FaFire } from "react-icons/fa";
import Header from "../components/Common/Header";
import Footer from "../components/Common/Footer";
import { analysisAPI, marketAPI } from "../functions/auth";
import Loader from "../components/Common/Loader";

// Register chart.js components
Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, TimeScale, Filler);

export default function AnalysisPage() {
  const [analysisData, setAnalysisData] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { symbol } = useParams();

  const getSourceName = (url) => {
    try {
        if (!url) return 'Unknown Source';
        const hostname = new URL(url).hostname.replace(/^www\./, '');
        const name = hostname.split('.')[0];
        return name.charAt(0).toUpperCase() + name.slice(1);
    } catch (e) {
        return 'Unknown Source';
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      if (!symbol) return;
      try {
        // Fetch both analysis and chart data in parallel
        const [analysisResult, chartResult] = await Promise.all([
          analysisAPI.getAnalysisResult(symbol),
          marketAPI.getCoinDetails(symbol)
        ]);

        console.log(analysisResult);
        console.log(chartResult);

        if (analysisResult) {
          setAnalysisData(analysisResult);
        }
        if (chartResult) {
          setChartData(chartResult);
        }
      } catch (error) {
        console.error("Error fetching page data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData(); // Initial fetch
    const intervalId = setInterval(fetchData, 30000); // Poll every 30 seconds
    return () => clearInterval(intervalId);
  }, [symbol]);

  const latestAnalysis = Array.isArray(analysisData) && analysisData.length > 0 
    ? analysisData[0] 
    : (analysisData || {});

  if (loading) {
    return (
      <div className="bg-black min-h-screen text-white flex flex-col">
        <Header />
        <div className="flex-grow flex flex-col items-center justify-center">
          <Loader />
          <p className="mt-4 text-lg">Loading Analysis...</p>
        </div>
        <Footer />
      </div>
    );
  }

  if (!latestAnalysis || Object.keys(latestAnalysis).length === 0) {
    return (
      <div className="bg-black min-h-screen text-white flex flex-col">
        <Header />
        <div className="flex-grow flex flex-col items-center justify-center">
          <div className="text-center">
            <FaExclamationTriangle className="mx-auto text-5xl text-blue mb-4" />
            <h2 className="text-2xl font-bold mb-2">Analysis Data Not Available</h2>
            <p className="text-grey">Waiting for the analysis workflow to generate data for {symbol?.toUpperCase()}.</p>
            <p className="text-grey text-sm mt-2">This page will update automatically.</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  // --- Safely destructure all data with fallbacks ---
  const { 
    sentiment_analysis = {}, 
    technical_analysis = {}, 
    strategy_analysis = {},
    prediction,
  } = latestAnalysis;

  // Correctly destructure nested technical analysis data
  const { 
    analysis: { 
      Quick_Stats = {}, 
      RSI = {}, 
      Indicator_Synthesis = {}, 
      Actionable_Takeaway = {},
      Trend_Analysis = {},
      Candles_and_EMA = {},
    } = {} 
  } = technical_analysis;
  
  const multi_timeframe_strategy = strategy_analysis.multi_timeframe_strategy || {};

  const prices = chartData?.chart_data?.['30'];
  const topicCounts = sentiment_analysis.topic_counts || {};

  // --- Chart Configurations ---

  const topicChartData = {
    labels: Object.keys(topicCounts),
    datasets: [{
      label: 'Mentions',
      data: Object.values(topicCounts),
      backgroundColor: 'rgba(58, 128, 233, 0.5)',
      borderColor: '#3a80e9',
      borderWidth: 1,
      borderRadius: 5,
    }]
  };

  const topicChartOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => `${context.raw} mentions`
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#888', beginAtZero: true },
        grid: { color: 'rgba(136, 136, 136, 0.2)' }
      },
      y: {
        ticks: { color: '#888' },
        grid: { color: 'transparent' }
      },
    },
  };

  const sentimentBarData = {
    labels: ["Extremely Bearish", "Bearish", "Neutral", "Bullish", "Extremely Bullish"],
    datasets: [
      {
        label: "Articles",
        data: [
          sentiment_analysis.extremely_bearish,
          sentiment_analysis.bearish,
          sentiment_analysis.neutral,
          sentiment_analysis.bullish,
          sentiment_analysis.extremely_bullish,
        ],
        backgroundColor: ['#f94141', '#87CEEB', '#888', '#61c96f', '#3a80e9'],
        borderRadius: 5,
      },
    ],
  };
  
  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { ticks: { color: '#888' }, grid: { color: 'rgba(136, 136, 136, 0.2)' } },
      x: { ticks: { color: '#888' }, grid: { color: 'rgba(136, 136, 136, 0.2)' } },
    },
  };

  const lineChartData = {
    labels: prices?.map(item => new Date(item[0])) || [],
    datasets: [{
      label: `${symbol?.toUpperCase()} Price (USD)`,
      data: prices?.map(item => item[1]) || [],
      borderColor: 'rgba(58, 128, 233, 0.8)',
      backgroundColor: 'rgba(58, 128, 233, 0.1)',
      tension: 0.3,
      fill: true,
      pointRadius: 0,
    }],
  };
  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y;
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'category',
        labels: prices?.map(item => new Date(item[0]).toLocaleDateString()) || [],
        ticks: { color: '#888' },
        grid: { color: 'rgba(136, 136, 136, 0.2)' },
      },
      y: {
        ticks: { color: '#888' },
        grid: { color: 'rgba(136, 136, 136, 0.2)' },
      },
    },
  };

  const getSentimentColor = (label) => {
    const l = label?.toLowerCase();
    if (l?.includes('bullish')) return 'text-green';
    if (l?.includes('bearish')) return 'text-red';
    return 'text-grey';
  }

  // Safely format any value (including objects/arrays) into a human readable string
  const formatValue = (value) => {
    if (value == null) return 'N/A';
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      return String(value);
    }
    if (Array.isArray(value)) {
      return value.map((v) => (typeof v === 'object' ? JSON.stringify(v) : String(v))).join(', ');
    }
    if (typeof value === 'object') {
      // Special handling for common indicator object shapes
      const hasPosition = Object.prototype.hasOwnProperty.call(value, 'position');
      const hasHistogram = Object.prototype.hasOwnProperty.call(value, 'histogram');
      if (hasPosition || hasHistogram) {
        const parts = [];
        if (hasPosition && value.position) parts.push(String(value.position));
        if (hasHistogram && value.histogram != null) parts.push(`histogram: ${value.histogram}`);
        return parts.join(' | ');
      }
      // Generic object pretty print
      try {
        return Object.entries(value)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : (typeof v === 'object' ? JSON.stringify(v) : String(v))}`)
          .join(' | ');
      } catch (e) {
        return JSON.stringify(value);
      }
    }
    return String(value);
  };

  return (
    <div className="bg-black min-h-screen text-white font-sans flex flex-col">
      <Header />
      <main className="flex-grow max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-4 mb-6">
          <img src={chartData?.logo} alt={`${symbol} logo`} className="w-12 h-12" />
          <div>
            <h1 className="text-4xl font-bold text-white tracking-tight">{chartData?.name} ({symbol?.toUpperCase()}) Analysis</h1>
            <p className="text-grey">Real-time analysis and market strategy</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8">
            <StatCard title="Current Price" value={chartData?.current_price && `$${chartData.current_price.toLocaleString()}`} />
            <StatCard title="Recommendation" value={Quick_Stats['Overall Recommendation']} />
            <StatCard title="Prediction" value={prediction === 1 ? "Bullish" : "Bearish"} color={prediction === 1 ? "text-green" : "text-red"} />
            <StatCard title="Confidence" value={sentiment_analysis.confidence_score && parseFloat(sentiment_analysis.confidence_score).toFixed(2)} />
            <StatCard title="Sentiment" value={sentiment_analysis.label} />
            <StatCard title="Sentiment Score" value={sentiment_analysis.score && parseFloat(sentiment_analysis.score).toFixed(2)} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
             {chartData && (
                <InfoCard title="Price History (30 Days)" icon={<FaChartBar />}>
                    <div className="h-96">
                        <Line data={lineChartData} options={lineChartOptions} />
                    </div>
                </InfoCard>
            )}
            {sentiment_analysis.recent_trends && (
            <div className="mt-8">
                <InfoCard title="Recent Trends & Outlook" icon={<FaNewspaper />}>
                    <div>
                      <h4 className="font-semibold text-white mb-1">Market Narrative</h4>
                      <p className="text-sm">{sentiment_analysis.recent_trends.description}</p>
                    </div>
                    <div className="mt-4">
                      <h4 className="font-semibold text-white mb-1">Future Outlook</h4>
                      <p className="text-sm">{sentiment_analysis.recent_trends.market_outlook}</p>
                    </div>
                </InfoCard>
            </div>
            )}
            <InfoCard title="Multi-Timeframe Strategy" icon={<FaBullseye />}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(multi_timeframe_strategy).map(([tf, strat]) => (
                  <div key={tf} className="bg-darkgrey/50 p-4 rounded-lg">
                    <h4 className="font-bold text-blue text-lg mb-2">{tf}</h4>
                    <ul className="space-y-2 text-sm text-grey">
                      <li><b>Outlook:</b> {strat.outlook}</li>
                      <li><b>Strategy:</b> {strat.strategy}</li>
                      <li><b>Entry:</b> {strat.entry_points?.join(", ")}</li>
                      <li><b>Exit:</b> {strat.exit_points?.join(", ")}</li>
                      <li><b>Risk:</b> {strat.risk_management}</li>
                    </ul>
                  </div>
                ))}
              </div>
            </InfoCard>
            <InfoCard title="Actionable Takeaways" icon={<FaBullseye />}>
                <div className="space-y-3 text-sm text-grey">
                    <p><strong>Market Bias:</strong> <span className={`font-bold ${getSentimentColor(Actionable_Takeaway['market_bias'])}`}>{Actionable_Takeaway['market_bias']}</span></p>
                    <p><strong>Next Steps:</strong> {Actionable_Takeaway['Next Steps']}</p>
                    <p><strong>Indicator Weight:</strong> {Actionable_Takeaway['indicator_weight']}</p>
                    <p><strong>External Prediction:</strong> {Actionable_Takeaway['external_prediction']}</p>
                </div>
            </InfoCard>
            <InfoCard title="Trend Analysis" icon={<FaChartBar />}>
                <ul className="space-y-2 text-sm text-grey">
                    <li><b>Trend Direction:</b> {Trend_Analysis?.trend_direction}</li>
                    <li><b>Candlestick Patterns:</b> {Trend_Analysis?.candlestick_patterns}</li>
                    <li><b>Volume Trends:</b> {Trend_Analysis?.volume_trends}</li>
                </ul>
            </InfoCard>
             <InfoCard title="Candles & EMA Analysis" icon={<FaChartBar />}>
                <ul className="space-y-2 text-sm text-grey">
                    <li><b>Analysis:</b> {Candles_and_EMA?.analysis}</li>
                    <li><b>Volume Behavior:</b> {Candles_and_EMA?.volume_behavior}</li>
                </ul>
            </InfoCard>
          </div>
          <div className="space-y-8">
            <InfoCard title="Sentiment Breakdown" icon={<FaChartBar />}>
              <div className="h-64">
                <Bar data={sentimentBarData} options={barOptions} />
              </div>
            </InfoCard>
            <InfoCard title="Hot Topics" icon={<FaFire />}>
              <div className="h-64">
                <Bar data={topicChartData} options={topicChartOptions} />
              </div>
            </InfoCard>
            <InfoCard title="Top 5 Articles" icon={<FaNewspaper />}>
              <ul className="space-y-3">
                {sentiment_analysis.top_articles?.slice(0, 5).map((article, i) => (
                  <li key={i} className="border-b border-grey last:border-0 pb-3 last:pb-0">
                    <a href={article.link} target="_blank" rel="noopener noreferrer" className="text-blue hover:underline font-medium cursor-pointer">
                      {article.title}
                    </a>
                    <div className="text-xs text-grey mt-1.5 flex items-center justify-between">
                      <span>{getSourceName(article.link)}</span>
                      <span>{new Date(article.pub_date).toLocaleDateString()}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </InfoCard>
            <InfoCard title="Technical Indicators" icon={<FaBrain />}>
                <ul className="space-y-3 text-sm">
                    <Indicator a="RSI" v={RSI && `${RSI['current_RSI_value']} (${RSI.interpretation})`} />
                    <Indicator a="MACD" v={formatValue(Indicator_Synthesis?.MACD)} />
                    <Indicator a="Bollinger Bands®" v={formatValue(Indicator_Synthesis && Indicator_Synthesis['Bollinger Bands'])} />
                    <Indicator a="Support/Resistance" v={formatValue(Indicator_Synthesis && Indicator_Synthesis['Support/Resistance'])} />
                    <Indicator a="Moving Averages" v={formatValue(Indicator_Synthesis && Indicator_Synthesis['Moving Averages (SMA & EMA)'])} />
                    <Indicator a="ATR" v={formatValue(Indicator_Synthesis && Indicator_Synthesis['ATR'])} />
                </ul>
            </InfoCard>
            <InfoCard title="Key Signals" icon={<FaExclamationTriangle />}>
                {technical_analysis?.bullish_signals && technical_analysis.bullish_signals.length > 0 && (
                  <div>
                    <h4 className="font-bold text-green mb-2">Bullish Signals</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-grey">
                      {technical_analysis.bullish_signals.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
                 {technical_analysis?.bearish_signals && technical_analysis.bearish_signals.length > 0 && (
                   <div className="mt-4">
                    <h4 className="font-bold text-red mb-2">Bearish Signals</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-grey">
                      {technical_analysis.bearish_signals.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                 )}
                {sentiment_analysis?.sentiment_drivers && sentiment_analysis.sentiment_drivers.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-bold text-blue mb-2">Sentiment Drivers</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-grey">
                      {sentiment_analysis.sentiment_drivers.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
                {strategy_analysis?.key_factors && strategy_analysis.key_factors.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-bold text-yellow-400 mb-2">Key Strategy Factors</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-grey">
                      {strategy_analysis.key_factors.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
            </InfoCard>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

// --- Helper Components ---
const StatCard = ({ title, value, color = 'text-white' }) => (
    <div className="bg-darkgrey p-4 rounded-lg shadow-md text-center">
        <p className="text-sm text-grey mb-1 truncate">{title}</p>
        <p className={`text-xl font-bold ${color}`}>{value || 'N/A'}</p>
    </div>
);

const InfoCard = ({ title, icon, children }) => (
  <div className="bg-darkgrey rounded-lg shadow-lg p-6">
    <div className="flex items-center space-x-3 mb-4">
      <span className="text-blue text-xl">{icon}</span>
      <h2 className="text-xl font-bold text-white">{title}</h2>
    </div>
    <div>{children}</div>
  </div>
);

const Indicator = ({ a, v }) => (
    <li className="flex justify-between items-center border-b border-grey pb-2">
        <span className="text-grey">{a}</span>
        <span className="text-right text-white font-medium">{v || 'N/A'}</span>
    </li>
);