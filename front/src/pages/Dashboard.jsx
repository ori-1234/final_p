import React, { useEffect, useRef, useState } from 'react';
import Header from '../components/Common/Header';
import TabsComponent from '../components/Dashboard/Tabs';
import Search from '../components/Dashboard/Search';
import PaginationComponent from '../components/Dashboard/Pagination';
import Loader from '../components/Common/Loader';
import BackToTop from '../components/Common/BackToTop';
import { marketAPI } from '../functions/auth';
import Footer from '../components/Common/Footer';

function DashboardPage() {
  const [coins, setCoins] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;
    getData();
  }, []);

  async function getData() {
    try {
      const data = await marketAPI.getMarketOverview();
      const d = JSON.stringify(data, null, 2)
      console.log(`ori data: ${JSON.parse(d)}`);

      if (Array.isArray(data)) {
        setCoins(data);
      } else {
        setCoins([]); // Ensure it's always an array
      }
      setIsLoading(false);
    } catch (e) {
      console.error('Error fetching data:', e);
      setIsLoading(false);
    }
  }

  const handlePageChange = (e, value) => {
    setPage(value);
  };

  const onSearchChange = (e) => {
    setSearch(e.target.value);
  };

  // Ensure coins is an array before filtering
  const filteredCoins = coins?.length
    ? coins.filter(
        (item) =>
          item.name?.toLowerCase().includes(search.toLowerCase()) ||
          item.symbol?.toLowerCase().includes(search.toLowerCase())
      )
    : [];

  // Pagination settings
  const itemsPerPage = 10;
  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedCoins = filteredCoins.slice(startIndex, endIndex);

  return (
    <>
      <Header />
      {isLoading ? (
        <Loader />
      ) : (
        <div className="min-h-screen">
          <BackToTop />

          <Search search={search} onSearchChange={onSearchChange} />
          <TabsComponent coins={search ? filteredCoins : paginatedCoins} />

          {!search && (
            <PaginationComponent page={page} handlePageChange={handlePageChange} />
          )}
        </div>
      )}
      <Footer />
    </>
  );
}

export default DashboardPage;

