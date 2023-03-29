import {
  Grid,
  Box,
  Card,
  Typography,
  Divider,
  Tooltip,
  Stack,
  IconButton,
  Avatar,
  alpha,
  styled,
  useTheme
} from '@mui/material';

import { useTranslation } from 'react-i18next';
import ApiTwoToneIcon from '@mui/icons-material/ApiTwoTone';
import LibraryBooksTwoToneIcon from '@mui/icons-material/LibraryBooksTwoTone';
import ArrowDownwardTwoToneIcon from '@mui/icons-material/ArrowDownwardTwoTone';
import ArrowUpwardTwoToneIcon from '@mui/icons-material/ArrowUpwardTwoTone';
import ThumbUpTwoToneIcon from '@mui/icons-material/ThumbUpTwoTone';
import CompareArrowsTwoToneIcon from '@mui/icons-material/CompareArrowsTwoTone';
import AddAlertTwoToneIcon from '@mui/icons-material/AddAlertTwoTone';
import Text from '../Text';
import PersonTwoToneIcon from '@mui/icons-material/PersonTwoTone';
import SubscriptionsTwoToneIcon from '@mui/icons-material/SubscriptionsTwoTone';
import MonetizationOnTwoToneIcon from '@mui/icons-material/MonetizationOnTwoTone';
import MoneyTwoToneIcon from '@mui/icons-material/MoneyTwoTone';
import CountUp from 'react-countup';
import AddCircleTwoToneIcon from '@mui/icons-material/AddCircleTwoTone';
import AddLocationTwoToneIcon from '@mui/icons-material/AddLocationTwoTone';
import AddBusinessTwoToneIcon from '@mui/icons-material/AddBusinessTwoTone';

const IconButtonWrapper = styled(IconButton)(
  ({ theme }) => `
    padding: ${theme.spacing(1.5)};
    color: ${theme.palette.primary.contrastText};
    transform: translateY(0px);
    transition: ${theme.transitions.create([
      'color',
      'transform',
      'background'
    ])};
    
    .MuiSvgIcon-root {
        transform: scale(1);
        transition: ${theme.transitions.create(['transform'])};
    }

    &:hover {
        background: initial;
        transform: translateY(-2px);

        .MuiSvgIcon-root {
            transform: scale(1.2);
        }
    }
  `
);

function Block1() {
  const { t } = useTranslation();
  const theme = useTheme();

  return (
    <div>
    <Typography variant="h6" component="h6" gutterBottom >
                  {'Ownership'}
       </Typography>

    <Grid container spacing={1}>
       
      <Grid item xs={12} md={6}>
        <Card
          sx={{
            p: 2.5,
            background: `${theme.colors.gradients.black1}`
          }}
        >
          <Box
            pb={2}
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Box>
              <Typography
                gutterBottom
                component="div"
                variant="caption"
                sx={{
                  color: `${theme.colors.alpha.trueWhite[70]}`
                }}
              >
                {t('Services')}
              </Typography>
              <Typography
                variant="h3"
                sx={{
                  color: `${theme.colors.alpha.trueWhite[100]}`
                }}
              >
               20
              </Typography>
            </Box>
            <Avatar
              variant="rounded"
              sx={{
                width: `${theme.spacing(7)}`,
                height: `${theme.spacing(7)}`,
                background: `${theme.colors.alpha.trueWhite[100]}`,
                color: `${theme.colors.success.main}`
              }}
            >
              <ApiTwoToneIcon />
            </Avatar>
          </Box>
          <Box display="flex" alignItems="center">
            <Typography
              variant="subtitle2"
              sx={{
                display: 'flex',
                alignItems: 'center',
                pr: 0.5,
                color: `${theme.colors.success.main}`
              }}
            >
              <ArrowUpwardTwoToneIcon
                fontSize="small"
                sx={{
                  mr: 0.2
                }}
              />
              <span>16.5%</span>
            </Typography>
            <Typography
              variant="subtitle2"
              noWrap
              sx={{
                color: `${theme.colors.alpha.trueWhite[70]}`
              }}
            >
              {t('increase this month')}
            </Typography>
          </Box>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card
          sx={{
            p: 2.5,
            background: `${theme.colors.gradients.blue4}`
          }}
        >
          <Box
            pb={2}
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Box>
              <Typography
                gutterBottom
                component="div"
                variant="caption"
                sx={{
                  color: `${theme.colors.alpha.trueWhite[70]}`
                }}
              >
                {t('New Libraries')}
              </Typography>
              <Typography
                variant="h3"
                sx={{
                  color: `${theme.colors.alpha.trueWhite[100]}`
                }}
              >
                200
              </Typography>
            </Box>
            <Avatar
              variant="rounded"
              sx={{
                width: `${theme.spacing(7)}`,
                height: `${theme.spacing(7)}`,
                background: `${theme.colors.alpha.trueWhite[100]}`,
                color: `${theme.colors.warning.main}`
              }}
            >
              <LibraryBooksTwoToneIcon />
            </Avatar>
          </Box>
          <Box display="flex" alignItems="center">
            <Typography
              variant="subtitle2"
              sx={{
                display: 'flex',
                alignItems: 'center',
                pr: 0.5,
                color: `${theme.colors.error.main}`
              }}
            >
              <ArrowDownwardTwoToneIcon
                fontSize="small"
                sx={{
                  mr: 0.2
                }}
              />
              <span>8.25%</span>
            </Typography>
            <Typography
              variant="subtitle2"
              noWrap
              sx={{
                color: `${theme.colors.alpha.trueWhite[70]}`
              }}
            >
              {t('decrease in numbers')}
            </Typography>
          </Box>
        </Card>
      </Grid>
     
    </Grid>
    </div>
  );
}

export default Block1;
