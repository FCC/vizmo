-- table vizmo_cdmacelllocation
DROP INDEX IF EXISTS oet_mba.vizmo_cdmacelllocation_submission_id_idx;
CREATE INDEX vizmo_cdmacelllocation_submission_id_idx
  ON oet_mba.vizmo_cdmacelllocation
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_cdmacelllocation_localdtime_idx;
CREATE INDEX vizmo_cdmacelllocation_localdtime_idx
  ON oet_mba.vizmo_cdmacelllocation
  USING btree
  (localdtime);
  
DROP INDEX IF EXISTS oet_mba.vizmo_cdmacelllocation_block_idx;
CREATE INDEX vizmo_cdmacelllocation_block_idx
  ON oet_mba.vizmo_cdmacelllocation
  USING btree
  (block);
  
DROP INDEX IF EXISTS oet_mba.vizmo_cdmacelllocation_cma_idx;
CREATE INDEX vizmo_cdmacelllocation_cma_idx
  ON oet_mba.vizmo_cdmacelllocation
  USING btree
  (cma);

DROP INDEX IF EXISTS oet_mba.vizmo_cdmacelllocation_geom_idx;
CREATE INDEX vizmo_cdmacelllocation_geom_idx
  ON oet_mba.vizmo_cdmacelllocation
  USING gist
  (geom); 

  
-- table vizmo_cellneighbourtower
DROP INDEX IF EXISTS oet_mba.vizmo_cellneighbourtower_submission_id_idx;
CREATE INDEX vizmo_cellneighbourtower_submission_id_idx
  ON oet_mba.vizmo_cellneighbourtower
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_cellneighbourtower_localdtime_idx;
CREATE INDEX vizmo_cellneighbourtower_localdtime_idx
  ON oet_mba.vizmo_cellneighbourtower
  USING btree
  (localdtime);
  

-- table vizmo_closesttarget
DROP INDEX IF EXISTS oet_mba.vizmo_closesttarget_submission_id_idx;
CREATE INDEX vizmo_closesttarget_submission_id_idx
  ON oet_mba.vizmo_closesttarget
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_closesttarget_localdtime_idx;
CREATE INDEX vizmo_closesttarget_localdtime_idx
  ON oet_mba.vizmo_closesttarget
  USING btree
  (localdtime);
  
  
-- table vizmo_cpuactivity
DROP INDEX IF EXISTS oet_mba.vizmo_cpuactivity_submission_id_idx;
CREATE INDEX vizmo_cpuactivity_submission_id_idx
  ON oet_mba.vizmo_cpuactivity
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_cpuactivity_localdtime_idx;
CREATE INDEX vizmo_cpuactivity_localdtime_idx
  ON oet_mba.vizmo_cpuactivity
  USING btree
  (localdtime);

  
-- table vizmo_datacap
DROP INDEX IF EXISTS oet_mba.vizmo_datacap_submission_id_idx;
CREATE INDEX vizmo_datacap_submission_id_idx
  ON oet_mba.vizmo_datacap
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_datacap_localdtime_idx;
CREATE INDEX vizmo_datacap_localdtime_idx
  ON oet_mba.vizmo_datacap
  USING btree
  (localdtime);
  
 
 -- table vizmo_gsmcelllocation
DROP INDEX IF EXISTS oet_mba.vizmo_gsmcelllocation_submission_id_idx;
CREATE INDEX vizmo_gsmcelllocation_submission_id_idx
  ON oet_mba.vizmo_gsmcelllocation
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_gsmcelllocation_localdtime_idx;
CREATE INDEX vizmo_gsmcelllocation_localdtime_idx
  ON oet_mba.vizmo_gsmcelllocation
  USING btree
  (localdtime);
  
-- table vizmo_httpget
DROP INDEX IF EXISTS oet_mba.vizmo_httpget_submission_id_idx;
CREATE INDEX vizmo_httpget_submission_id_idx
  ON oet_mba.vizmo_httpget
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_httpget_localdtime_idx;
CREATE INDEX vizmo_httpget_localdtime_idx
  ON oet_mba.vizmo_httpget
  USING btree
  (localdtime);
  

-- table vizmo_httppost
DROP INDEX IF EXISTS oet_mba.vizmo_httppost_submission_id_idx;
CREATE INDEX vizmo_httppost_submission_id_idx
  ON oet_mba.vizmo_httppost
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_httppost_localdtime_idx;
CREATE INDEX vizmo_httppost_localdtime_idx
  ON oet_mba.vizmo_httppost
  USING btree
  (localdtime);
  
  
-- table vizmo_location
DROP INDEX IF EXISTS oet_mba.vizmo_location_submission_id_idx;
CREATE INDEX vizmo_location_submission_id_idx
  ON oet_mba.vizmo_location
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_location_localdtime_idx;
CREATE INDEX vizmo_location_localdtime_idx
  ON oet_mba.vizmo_location
  USING btree
  (localdtime);
  
DROP INDEX IF EXISTS oet_mba.vizmo_location_block_idx;
CREATE INDEX vizmo_location_block_idx
  ON oet_mba.vizmo_location
  USING btree
  (block);
  
DROP INDEX IF EXISTS oet_mba.vizmo_location_cma_idx;
CREATE INDEX vizmo_location_cma_idx
  ON oet_mba.vizmo_location
  USING btree
  (cma);

DROP INDEX IF EXISTS oet_mba.vizmo_location_geom_idx;
CREATE INDEX vizmo_location_geom_idx
  ON oet_mba.vizmo_location
  USING gist
  (geom); 
  

-- table vizmo_netactivity
DROP INDEX IF EXISTS oet_mba.vizmo_netactivity_submission_id_idx;
CREATE INDEX vizmo_netactivity_submission_id_idx
  ON oet_mba.vizmo_netactivity
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_netactivity_localdtime_idx;
CREATE INDEX vizmo_netactivity_localdtime_idx
  ON oet_mba.vizmo_netactivity
  USING btree
  (localdtime);


-- table vizmo_netusage
DROP INDEX IF EXISTS oet_mba.vizmo_netusage_submission_id_idx;
CREATE INDEX vizmo_netusage_submission_id_idx
  ON oet_mba.vizmo_netusage
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_netusage_localdtime_idx;
CREATE INDEX vizmo_netusage_localdtime_idx
  ON oet_mba.vizmo_netusage
  USING btree
  (localdtime);

  
-- table vizmo_networkdata
DROP INDEX IF EXISTS oet_mba.vizmo_networkdata_submission_id_idx;
CREATE INDEX vizmo_networkdata_submission_id_idx
  ON oet_mba.vizmo_networkdata
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_networkdata_localdtime_idx;
CREATE INDEX vizmo_networkdata_localdtime_idx
  ON oet_mba.vizmo_networkdata
  USING btree
  (localdtime);
  
  
-- table vizmo_submission
DROP INDEX IF EXISTS oet_mba.vizmo_submission_submission_id_idx;
CREATE INDEX vizmo_submission_submission_id_idx
  ON oet_mba.vizmo_submission
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_submission_localdtime_idx;
CREATE INDEX vizmo_submission_localdtime_idx
  ON oet_mba.vizmo_submission
  USING btree
  (localdtime);
  
DROP INDEX IF EXISTS oet_mba.vizmo_submission_manufacturer_idx;
CREATE INDEX vizmo_submission_manufacturer_idx
  ON oet_mba.vizmo_submission
  USING btree
  (manufacturer);
  
DROP INDEX IF EXISTS oet_mba.vizmo_submission_model_idx;
CREATE INDEX vizmo_submission_model_idx
  ON oet_mba.vizmo_submission
  USING btree
  (model);
  
DROP INDEX IF EXISTS oet_mba.vizmo_submission_os_type_idx;
CREATE INDEX vizmo_submission_os_type_idx
  ON oet_mba.vizmo_submission
  USING btree
  (os_type);
  
DROP INDEX IF EXISTS oet_mba.vizmo_submission_os_version_idx;
CREATE INDEX vizmo_submission_os_version_idx
  ON oet_mba.vizmo_submission
  USING btree
  (os_version);
  

-- table vizmo_udplatency
DROP INDEX IF EXISTS oet_mba.vizmo_udplatency_submission_id_idx;
CREATE INDEX vizmo_udplatency_submission_id_idx
  ON oet_mba.vizmo_udplatency
  USING btree
  (submission_id);
  
DROP INDEX IF EXISTS oet_mba.vizmo_udplatency_localdtime_idx;
CREATE INDEX vizmo_udplatency_localdtime_idx
  ON oet_mba.vizmo_udplatency
  USING btree
  (localdtime);
