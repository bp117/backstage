import { Box, Card, Grid, Typography, useTheme } from '@mui/material';

import Chart from 'react-apexcharts';

import KeyboardArrowDownTwoToneIcon from '@mui/icons-material/KeyboardArrowDownTwoTone';
import KeyboardArrowUpTwoToneIcon from '@mui/icons-material/KeyboardArrowUpTwoTone';

function Block5() {
  const theme = useTheme();

  const chart1Options = {
    chart: {
      background: 'transparent',
      toolbar: {
        show: false
      },
      sparkline: {
        enabled: true
      }
    },
    theme: {
      mode: theme.palette.mode === 'dark' ? 'light' : 'dark'
    },
    stroke: {
      colors: [theme.colors.warning.main],
      width: 3
    },
    colors: [theme.colors.warning.main],
    markers: {
      size: 0
    },
    grid: {
      padding: {
        right: 5,
        left: 5
      }
    },
    tooltip: {
      fixed: {
        enabled: true
      },
      x: {
        show: false
      },
      y: {
        title: {
          formatter() {
            return '$';
          }
        }
      },
      marker: {
        show: false
      }
    },
    yaxis: {
      show: false
    },
    legend: {
      show: false
    }
  };
  const chart1Data = [
    {
      name: 'Bitcoin',
      data: [47, 38, 56, 24, 56, 24, 65]
    }
  ];

  const chart2Options = {
    chart: {
      background: 'transparent',
      toolbar: {
        show: false
      },
      sparkline: {
        enabled: true
      }
    },
    theme: {
      mode: theme.palette.mode === 'dark' ? 'light' : 'dark'
    },
    stroke: {
      colors: [theme.colors.error.main],
      width: 3
    },
    colors: [theme.colors.error.main],
    markers: {
      size: 0
    },
    grid: {
      padding: {
        right: 5,
        left: 5
      }
    },
    tooltip: {
      fixed: {
        enabled: true
      },
      x: {
        show: false
      },
      y: {
        title: {
          formatter() {
            return '$';
          }
        }
      },
      marker: {
        show: false
      }
    },
    legend: {
      show: false
    }
  };
  const chart2Data = [
    {
      name: 'Cardano',
      data: [38, 44, 56, 47, 26, 24, 45]
    }
  ];

  const chart3Options = {
    chart: {
      background: 'transparent',
      toolbar: {
        show: false
      },
      sparkline: {
        enabled: true
      }
    },
    theme: {
      mode: theme.palette.mode === 'dark' ? 'light' : 'dark'
    },
    stroke: {
      colors: [theme.colors.success.main],
      width: 3
    },
    colors: [theme.colors.success.main],
    markers: {
      size: 0
    },
    grid: {
      padding: {
        right: 5,
        left: 5
      }
    },
    tooltip: {
      fixed: {
        enabled: true
      },
      x: {
        show: false
      },
      y: {
        title: {
          formatter() {
            return '$';
          }
        }
      },
      marker: {
        show: false
      }
    },
    legend: {
      show: false
    }
  };
  const chart3Data = [
    {
      name: 'Ethereum',
      data: [38, 43, 24, 56, 35, 56, 65]
    }
  ];

  const chart4Options = {
    chart: {
      background: 'transparent',
      toolbar: {
        show: false
      },
      sparkline: {
        enabled: true
      }
    },
    theme: {
      mode: theme.palette.mode === 'dark' ? 'light' : 'dark'
    },
    stroke: {
      colors: [theme.colors.info.main],
      width: 3
    },
    colors: [theme.colors.info.main],
    markers: {
      size: 0
    },
    grid: {
      padding: {
        right: 5,
        left: 5
      }
    },
    tooltip: {
      fixed: {
        enabled: true
      },
      x: {
        show: false
      },
      y: {
        title: {
          formatter() {
            return '$';
          }
        }
      },
      marker: {
        show: false
      }
    },
    legend: {
      show: false
    }
  };
  const chart4Data = [
    {
      name: 'Ripple',
      data: [33, 56, 24, 23, 24, 65, 43]
    }
  ];

  return (
    <div>
    <Typography variant="h6" component="h6" gutterBottom >
                  {'Metrics'}
       </Typography>

    <Grid container spacing={4}>
      <Grid item xs={12} md={6}>
        <Card
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 2.5
          }}
        >
          <Box>
            <Typography
              variant="caption"
              sx={{
                fontWeight: 'bold'
              }}
            >
              Codesmells
            </Typography>
            <Typography
              variant="h5"
              sx={{
                pb: 1,
                pt: 0.5,
                lineHeight: 1,
                display: 'flex',
                alignItems: 'center',
                color: `${theme.colors.success.main}`
              }}
            >
              <span>54%</span>
              <KeyboardArrowUpTwoToneIcon fontSize="small" />
            </Typography>
            <Typography variant="h3">8,583</Typography>
          </Box>
          <Box ml={2} flexGrow={1}>
            <Chart
              options={chart1Options}
              series={chart1Data}
              type="line"
              height={80}
            />
          </Box>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 2.5
          }}
        >
          <Box>
            <Typography
              variant="caption"
              sx={{
                fontWeight: 'bold'
              }}
            >
              Vulnerabilities
            </Typography>
            <Typography
              variant="h5"
              sx={{
                pb: 1,
                pt: 0.5,
                lineHeight: 1,
                display: 'flex',
                alignItems: 'center',
                color: `${theme.colors.success.main}`
              }}
            >
              <span>21%</span>
              <KeyboardArrowUpTwoToneIcon fontSize="small" />
            </Typography>
            <Typography variant="h3">21</Typography>
          </Box>
          <Box ml={2} flexGrow={1}>
            <Chart
              options={chart2Options}
              series={chart2Data}
              type="line"
              height={80}
            />
          </Box>
        </Card>
      </Grid>
     
    </Grid>
    </div>
  );
}

export default Block5;
