// K(1000 - 999,999) , M(1,000,000 - 999,999,999) , B(1,000,000,000 - 999,999,999,999)

export const convertNums = (num) => {
    if (num < 1000) {
        return num.toLocaleString(2);
    } else if (num < 1000000) {
        return `${(num / 1000).toFixed(1)}K`;
    } else if (num < 1000000000) {
        return `${(num / 1000000).toFixed(1)}M`;
    } else {
        return `${(num / 1000000000).toFixed(1)}B`;
    }
 
}