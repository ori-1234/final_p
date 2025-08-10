function SelectCoin({ crypto1, crypto2, handleCoinChange, availableCoins }) {
    return (
        <div className='flex flex-row items-center gap-14 pl-2 m-4'>
            <div className='flex flex-row items-center gap-2'>
                <p>Crypto 1</p>
                <select
                    value={crypto1}
                    onChange={(e) => handleCoinChange(e, true)}
                    className="p-2 rounded bg-gray-800 text-white outline-none"
                >
                    {availableCoins.map((coin) => (
                        <option 
                            key={coin} 
                            value={coin}
                            disabled={coin === crypto2}
                        >
                            {coin}
                        </option>
                    ))}
                </select>
            </div>

            <div className='flex flex-row items-center gap-2'>
                <p>Crypto 2</p>
                <select
                    value={crypto2}
                    onChange={(e) => handleCoinChange(e, false)}
                    className="p-2 rounded bg-gray-800 text-white outline-none"
                >
                    {availableCoins.map((coin) => (
                        <option 
                            key={coin} 
                            value={coin}
                            disabled={coin === crypto1}
                        >
                            {coin}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
}

export default SelectCoin;