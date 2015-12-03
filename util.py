import os
import dataset
from datetime import datetime

db = os.environ.get('DATABASE_URI', 'sqlite:///data.sqlite')
engine = dataset.connect(db)

reg_person = engine['eu_tr_person']
reg_financial_data = engine['eu_tr_financial_data']
reg_financial_data_custom_source = engine['eu_tr_financial_data_custom_source']
reg_financial_data_turnover = engine['eu_tr_financial_data_turnover']
reg_representative = engine['eu_tr_representative']
reg_organisation = engine['eu_tr_organisation']
reg_action_field = engine['eu_tr_action_field']
reg_interest = engine['eu_tr_interest']
reg_country_of_member = engine['eu_tr_country_of_member']


def dateconv(ds):
    if ds is not None:
        return datetime.strptime(ds.split("+")[0], "%Y-%m-%dT%H:%M:%S.%f")


def shortdateconv(ds):
    return datetime.strptime(ds, "%Y-%m-%d+%H:%M")


def intconv(val):
    return val
