import React from 'react';
import PageHeader from './PageHeader';
import Footer from '../Footer';
import PageTitleWrapper from '../PageTitleWrapper';

import { Grid } from '@mui/material';
import Block1 from './Block1';
import Block2 from './Block2';
import Block3 from './Block3';
//import Block4 from 'src/content/blocks/SparklinesLarge/Block6';
import Block5 from './Block5';
import { Typography } from '@material-ui/core';
//import Block6 from 'src/content/blocks/Grids/Block5';
//import Block7 from 'src/content/blocks/IconCards/Block4';
import ResourcesAlarm from './ResourcesAlarm';
import HealthStatus from './HealthStatus';
import ServicesByCategory from './ServicesByCategory';
import LibsByCategory from './LibsByCategory';
export const HomePage = () => {
  /* We will shortly compose a pretty homepage here. */
  return (
    <>
     
        <title>Dashboard</title>
     
      <PageTitleWrapper>
        <PageHeader />
      </PageTitleWrapper>
      <div>
        <Typography variant="h6" component="h6" gutterBottom >
                  {'Ownership'}
       </Typography>
       </div>
      <Grid
        sx={{
          px: 4
        }}
        container
        direction="row"
        justifyContent="left"
        alignItems="stretch"
        spacing={3}
      >
       
        <Grid item xs={12} md={6} >
          <ServicesByCategory />
        </Grid>
        <Grid item xs={12} md={6} >
          <LibsByCategory />
        </Grid>
           
        <Grid item xs={12} md={6}>
            <Block5 />
        </Grid>
        <Grid item xs={12} md={6}>
          <ResourcesAlarm />
        </Grid>
        <Grid item xs={12} md={6}>
          <HealthStatus />
        </Grid>   
       
      </Grid>
     
    </>
  );
};