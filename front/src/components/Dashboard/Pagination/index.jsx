import React, { useState } from "react";
import "./styles.css";

import Pagination from "@mui/material/Pagination";

export default function PaginationComponent({ page, handlePageChange }) {
  return (
    <div className="pagination-div">
      <Pagination
        count={1}
        page={page}
        onChange={handlePageChange}

        sx={{
          "& .MuiPaginationItem-text": {
            color: "#fff !important",
            border: "1px solid #888",
          },
          "& .MuiPaginationItem-text:hover": {
            backgroundColor: "transparent !important",
          },
          "& .Mui-selected  ": {
            backgroundColor: "#3a80e9",
            borderColor: "#3a80e9",
          },
          "& .MuiPaginationItem-ellipsis": {
            border: "none",
          },
        }}
      />
    </div>
  );
}