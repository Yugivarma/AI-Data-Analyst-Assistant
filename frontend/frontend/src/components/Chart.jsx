import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function formatLabel(value) {
  if (!value) {
    return "";
  }

  return String(value)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNumber(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return value;
  }

  return number.toLocaleString("en-US", {
    maximumFractionDigits: 2,
  });
}

function formatCurrency(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return value;
  }

  return `$${number.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) {
    return null;
  }

  return (
    <div className="custom-tooltip">
      <p className="tooltip-label">
        {formatLabel(label)}
      </p>

      {payload.map((entry, index) => {
        const value = entry.value;
        const dataKey = entry.dataKey;

        const isCurrency =
          String(dataKey).toLowerCase().includes("revenue") ||
          String(dataKey).toLowerCase().includes("spend") ||
          String(dataKey).toLowerCase().includes("price") ||
          String(dataKey).toLowerCase().includes("value");

        return (
          <p
            className="tooltip-value"
            key={index}
          >
            {formatLabel(dataKey)}:{" "}
            <strong>
              {isCurrency
                ? formatCurrency(value)
                : formatNumber(value)}
            </strong>
          </p>
        );
      })}
    </div>
  );
}

function Chart({ visualization }) {
  if (
    !visualization ||
    !visualization.data ||
    visualization.data.length === 0
  ) {
    return (
      <div className="placeholder">
        No visualization data available.
      </div>
    );
  }

  const {
    type,
    x_key,
    y_key,
    data,
  } = visualization;

  const chartData = data.map((row) => ({
    ...row,
    [y_key]: Number(row[y_key]),
  }));

  /*
   * LINE CHART
   */

  if (type === "line") {
    return (
      <div className="chart-container">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart
            data={chartData}
            margin={{
              top: 20,
              right: 30,
              left: 10,
              bottom: 60,
            }}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey={x_key}
              tickFormatter={formatLabel}
              angle={-30}
              textAnchor="end"
              interval={0}
              height={70}
              tick={{ fontSize: 12 }}
            />

            <YAxis
              tickFormatter={formatNumber}
              tick={{ fontSize: 12 }}
            />

            <Tooltip
              content={<CustomTooltip />}
            />

            <Legend />

            <Line
              type="monotone"
              dataKey={y_key}
              name={formatLabel(y_key)}
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />

          </LineChart>
        </ResponsiveContainer>

      </div>
    );
  }

  /*
   * PIE CHART
   */

  if (type === "pie") {
    return (
      <div className="chart-container">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <PieChart>

            <Pie
              data={chartData}
              dataKey={y_key}
              nameKey={x_key}
              cx="50%"
              cy="48%"
              outerRadius={145}
              innerRadius={65}
              paddingAngle={2}
              label={({ name, percent }) =>
                `${formatLabel(name)} ${(percent * 100).toFixed(0)}%`
              }
              labelLine={true}
            >

              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                />
              ))}

            </Pie>

            <Tooltip
              content={<CustomTooltip />}
            />

            <Legend
              formatter={(value) =>
                formatLabel(value)
              }
            />

          </PieChart>
        </ResponsiveContainer>

      </div>
    );
  }

  /*
   * TABLE FALLBACK
   */

  if (type === "table") {
    return (
      <div className="placeholder">
        The results are best displayed as a table.
      </div>
    );
  }

  /*
   * BAR CHART
   */

  return (
    <div className="chart-container">

      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <BarChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 10,
            bottom: 70,
          }}
        >

          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
          />

          <XAxis
            dataKey={x_key}
            tickFormatter={formatLabel}
            angle={-30}
            textAnchor="end"
            interval={0}
            height={80}
            tick={{ fontSize: 12 }}
          />

          <YAxis
            tickFormatter={formatNumber}
            tick={{ fontSize: 12 }}
          />

          <Tooltip
            content={<CustomTooltip />}
            cursor={{ opacity: 0.08 }}
          />

          <Legend
            formatter={(value) =>
              formatLabel(value)
            }
          />

          <Bar
            dataKey={y_key}
            name={formatLabel(y_key)}
            radius={[6, 6, 0, 0]}
            maxBarSize={60}
          />

        </BarChart>
      </ResponsiveContainer>

    </div>
  );
}

export default Chart;