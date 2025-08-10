import React from 'react';
import { useNavigate } from 'react-router-dom';
import SparklineChart from './SparklineChart';

const AnalysisCard = ({ coin }) => {
  const navigate = useNavigate();

  const handleCardClick = () => {
    navigate(`/analysis/${coin.ticker.toLowerCase()}`);
  };

  const aiSummary = coin.sentiment_analysis?.recent_trends?.description || "AI summary is not available at the moment.";
  const truncatedSummary = aiSummary.length > 150 ? aiSummary.substring(0, 150) + '...' : aiSummary;

  const topicCounts = coin.sentiment_analysis?.topic_counts || {};
  const connectedWords = Object.entries(topicCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5)
    .map(([topic]) => topic);

  const name = coin.name || coin.ticker;
  const image = coin.logo;
  const chartData = coin.chart_data;

  return (
    <div 
      className="bg-darkgrey p-6 rounded-lg shadow-lg cursor-pointer transition-transform transform hover:scale-105"
      onClick={handleCardClick}
    >
      <div className="flex justify-between items-start">
        <div className="flex items-center space-x-4">
          {image && <img src={image} alt={`${name} logo`} className="w-10 h-10" />}
          <div>
            <h3 className="text-xl font-bold text-white">{name} ({coin.ticker?.toUpperCase()})</h3>
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
        <div className="md:col-span-1 h-24">
          {chartData && chartData.length > 0 ? (
            <SparklineChart data={chartData} />
          ) : (
            <div className="w-full h-full bg-grey/20 rounded flex items-center justify-center text-grey text-sm">Chart data not available</div>
          )}
        </div>

        <div className="md:col-span-2">
          <h4 className="font-semibold text-white mb-2">AI Summary</h4>
          <p className="text-sm text-grey">
            {truncatedSummary}
            {aiSummary.length > 150 && <span className="text-blue ml-1 cursor-pointer" onClick={(e) => {e.stopPropagation(); handleCardClick();}}>Read more</span>}
          </p>
        </div>
      </div>
        <div className="mt-4">
            <h4 className="font-semibold text-white mb-2">Connected words</h4>
            {connectedWords.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                    {connectedWords.map((word, index) => (
                        <span key={index} className="bg-blue/20 text-blue px-2 py-1 rounded-md text-xs">{word}</span>
                    ))}
                </div>
            ) : (
                <p className="text-sm text-grey">No connected words found.</p>
            )}
        </div>
    </div>
  );
};

export default AnalysisCard;
