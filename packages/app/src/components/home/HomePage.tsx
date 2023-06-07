import React from 'react';
import PageHeader from './PageHeader';
import PageTitleWrapper from '../PageTitleWrapper';

import { Grid } from '@mui/material';
import { Typography } from '@material-ui/core';
//import Block6 from 'src/content/blocks/Grids/Block5';
//import Block7 from 'src/content/blocks/IconCards/Block4';
import ResourcesAlarm from './ResourcesAlarm';
import HealthStatus from './HealthStatus';
import ServicesByCategory from './ServicesByCategory';
import LibsByCategory from './LibsByCategory';
import Migrations from './migrations';
import DrillDownChart from './drilldownblock';

export const HomePage = () => {
  /* We will shortly compose a pretty homepage here. */
  return (
    <>
     
        <title>Dashboard</title>
     
      <PageTitleWrapper>
        <PageHeader />
      </PageTitleWrapper>
    
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
          <ResourcesAlarm/>
        </Grid>
        <Grid item xs={12} md={6}>
          <HealthStatus />
        </Grid>   
           
        <Grid item xs={12} >
          <Typography variant="h5" component="h2" gutterBottom>
            Platform Migrations
          </Typography>


            <Migrations />
        </Grid>
       
      </Grid>
     
    </>
  );
};