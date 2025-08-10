import React, { useEffect, useState } from 'react';
import Header from '../components/Common/Header';
import Footer from '../components/Common/Footer';
import Loader from '../components/Common/Loader';
import AnalysisCard from '../components/Analysis/AnalysisCard';
import { marketAPI, analysisAPI } from '../functions/auth';

const AnalysisPage = () => {
  const [analysisList, setAnalysisList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysisData = async () => {
      try {
        const marketOverview = await marketAPI.getMarketOverview();

        if (Array.isArray(marketOverview)) {
          const mergedDataPromises = marketOverview.map(async (coin) => {
            try {
              const [details, analysis] = await Promise.all([
                marketAPI.getCoinDetails(coin.symbol),
                analysisAPI.getAnalysisResult(coin.symbol)
              ]);

              return {
                ...details,
                ticker: coin.symbol.toUpperCase(),
                chart_data: details?.chart_data?.['7'],
                sentiment_analysis: analysis?.sentiment_analysis || null,
                technical_analysis: analysis?.technical_analysis || null,
              };
            } catch (error) {
              console.error(`Failed to fetch data for ${coin.symbol}`, error);
              return null; // Return null for failed fetches
            }
          });

          const mergedData = (await Promise.all(mergedDataPromises)).filter(Boolean);
          setAnalysisList(mergedData);
        }
      } catch (error) {
        console.error("Error fetching analysis page data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, []);

  return (
    <div className="bg-black min-h-screen text-white">
      <Header />
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
            <h1 className="text-4xl font-bold tracking-tight">Social Dominance Analysis</h1>
        </div>

        {loading ? (
          <Loader />
        ) : (
          <div className="space-y-6">
            {analysisList.length > 0 ? (
              analysisList.map((item, index) => (
                <AnalysisCard key={item.ticker || index} coin={item} />
              ))
            ) : (
              <p>No analysis data available at the moment.</p>
            )}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default AnalysisPage;
