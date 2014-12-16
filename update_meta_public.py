import database

def create_meta_public():

    db_private = database.Connection('private')
    db_public = database.Connection('public')
    geo_bins_public = db_public.geo.bins

    bin_5k = geo_bins_public.find({'geo_type': 'hex5k'}).count()
    bin_10k = geo_bins_public.find({'geo_type': 'hex10k'}).count()
    bin_25k = geo_bins_public.find({'geo_type': 'hex25k'}).count()

    bin_county = geo_bins_public.find({'geo_type': 'county'}).count()
    bin_metro = geo_bins_public.find({'geo_type': 'metro'}).count()
    bin_state = geo_bins_public.find({'geo_type': 'state'}).count()
    bin_county = geo_bins_public.find({'geo_type': 'county'}).count()
    bin_total = bin_5k + bin_10k + bin_25k + + bin_county + bin_metro + bin_state 

    bin_att = 0
    bin_sprint = 0
    bin_tmobile = 0
    bin_verizon = 0
    bin_other = 0
    bin_combined = 0

    bins_coll = geo_bins_public.find()
    bin_combined = bins_coll.count()
    for b in bins_coll:
        if 'AT&T' in b['carriers']:
            bin_att += 1
        if 'Sprint' in b['carriers']:
            bin_sprint += 1
        if 'T-Mobile' in b['carriers']:
            bin_tmobile += 1
        if 'Verizon' in b['carriers']:
            bin_verizon += 1
        if 'Other' in b['carriers']:
            bin_other += 1


    meta_bins = {'type': 'bins', 'total': bin_total, 'geo': {'hex5k': bin_5k, 'hex10k': bin_10k, 'hex25k': bin_25k, 'county': bin_county, 'metro': bin_metro, 'state': bin_state}, 'carrier': {'combined': bin_combined, 'att': bin_att, 'sprint': bin_sprint, 'tmobile': bin_tmobile, 'verizon': bin_verizon, 'other': bin_other}}

    #aggregations
    aggregations_public = db_public.aggregations

    agg_total = aggregations_public.find().count()
    agg_5k = aggregations_public.find({'id.geo_type': 'hex5k'}).count()
    agg_10k = aggregations_public.find({'id.geo_type': 'hex10k'}).count()
    agg_25k = aggregations_public.find({'id.geo_type': 'hex25k'}).count()
    agg_county = aggregations_public.find({'id.geo_type': 'county'}).count()
    agg_metro = aggregations_public.find({'id.geo_type': 'metro'}).count()
    agg_state = aggregations_public.find({'id.geo_type': 'state'}).count()
    agg_combined = aggregations_public.find({'id.carrier': 'combined'}).count()
    agg_att = aggregations_public.find({'id.carrier': 'att'}).count()
    agg_sprint = aggregations_public.find({'id.carrier': 'sprint'}).count()
    agg_tmobile = aggregations_public.find({'id.carrier': 'tmobile'}).count()
    agg_verizon = aggregations_public.find({'id.carrier': 'verizon'}).count()
    agg_other = aggregations_public.find({'id.carrier': 'other'}).count()

    meta_aggregations = {'type': 'aggregations', 'total': agg_total, 'geo': {'hex5k': agg_5k, 'hex10k': agg_10k, 'hex25k': agg_25k, 'county': agg_county, 'metro': agg_metro, 'state': agg_state}, 'carrier': {'combined': agg_combined, 'att': agg_att, 'sprint': agg_sprint, 'tmobile': agg_tmobile, 'verizon': agg_verizon, 'other': agg_other}}

    dates = db_private.meta.find_one({'type': 'dates'})
    latest_imported = dates['latest_imported_date']
    latest_binned = dates['latest_binned_date']
    latest_aggregated = dates['latest_aggregated_date']

    meta_dates = {'type': 'dates', 'latest_imported': latest_imported, 'latest_binned': latest_binned, 'latest_aggregated': latest_aggregated}

    db_public.meta.public.drop()
    db_public.meta.public.insert(meta_bins)
    db_public.meta.public.insert(meta_aggregations)
    db_public.meta.public.insert(meta_dates)

if __name__ == "__main__":
    create_meta_public()






