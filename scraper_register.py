import sys
from lxml import etree
from datetime import datetime
# from pprint import pprint

import logging
import requests

from util import reg_person, reg_financial_data
from util import reg_representative, reg_organisation
from util import reg_action_field
from util import reg_interest, reg_country_of_member
from util import reg_financial_data_turnover
from util import reg_financial_data_custom_source
from util import dateconv, intconv

log = logging.getLogger('scraper_interests')
logging.basicConfig(level=logging.INFO)

URL = 'http://ec.europa.eu/transparencyregister/public/consultation/statistics.do?action=getLobbyistsXml&fileType=NEW'
NS2 = "{http://www.w3.org/1999/xlink}"
NS = "{http://intragate.ec.europa.eu/transparencyregister/intws/20141104}"
SI = "{http://www.w3.org/2001/XMLSchema-instance}"


def parse_rep(rep_el):
    rep = {}
    rep['identification_code'] = rep_el.findtext(NS + 'identificationCode')
    rep['status'] = rep_el.findtext(NS + 'status')
    rep['registration_date'] = dateconv(rep_el.findtext(NS + 'registrationDate'))
    rep['last_update_date'] = dateconv(rep_el.findtext(NS + 'lastUpdateDate'))
    rep['legal_status'] = rep_el.findtext(NS + 'legalStatus')
    rep['acronym'] = rep_el.findtext(NS + 'acronym')
    rep['original_name'] = rep_el.findtext('.//' + NS + 'originalName')
    el = rep_el.find(NS + 'webSiteURL')
    rep['web_site_url'] = el.get(NS2 + 'href') if el is not None else None
    rep['main_category'] = rep_el.findtext('.//' + NS + 'mainCategory')
    rep['sub_category'] = rep_el.findtext('.//' + NS + 'subCategory')

    legal = {}
    legal['title'] = rep_el.findtext(NS + 'legalResp/' + NS + 'title')
    legal['first_name'] = rep_el.findtext(NS + 'legalResp/' + NS + 'firstName')
    legal['last_name'] = rep_el.findtext(NS + 'legalResp/' + NS + 'lastName')
    legal['position'] = rep_el.findtext(NS + 'legalResp/' + NS + 'position')
    rep['legal_person'] = legal

    eu = {}
    eu['title'] = rep_el.findtext(NS + 'euRelationsResp/' + NS + 'title')
    eu['first_name'] = rep_el.findtext(NS + 'euRelationsResp/' + NS + 'firstName')
    eu['last_name'] = rep_el.findtext(NS + 'euRelationsResp/' + NS + 'lastName')
    eu['position'] = rep_el.findtext(NS + 'euRelationsResp/' + NS + 'position')
    rep['eu_person'] = eu

    rep['contact_street'] = rep_el.findtext(NS + 'contactDetails/' + NS + 'addressline1')
    rep['contact_number'] = rep_el.findtext(NS + 'contactDetails/' + NS + 'number')
    rep['contact_post_code'] = rep_el.findtext(NS + 'contactDetails/' + NS
            + 'postCode')
    rep['contact_town'] = rep_el.findtext(NS + 'contactDetails/' + NS
            + 'town')
    rep['contact_country'] = rep_el.findtext(NS + 'contactDetails/' + NS
            + 'country')
    rep['contact_indic_phone'] = rep_el.findtext(NS + 'contactDetails//' + NS
            + 'indicPhone')
    rep['contact_indic_fax'] = rep_el.findtext(NS + 'contactDetails//' + NS
            + 'indicFax')
    rep['contact_fax'] = rep_el.findtext(NS + 'contactDetails//' + NS
            + 'fax')
    rep['contact_phone'] = rep_el.findtext(NS + 'contactDetails//' + NS
            + 'phoneNumber')
    rep['contact_more'] = rep_el.findtext(NS + 'contactDetails/' + NS
            + 'moreContactDetails')

    rep['goals'] = rep_el.findtext(NS + 'goals')
    rep['networking'] = rep_el.findtext(NS + 'networking')

    # rep['activities'] = rep_el.findtext(NS + 'activities')
    act_el = rep_el.find(NS + 'activities')
    if act_el is not None:
        rep['activity_eu_legislative'] = act_el.findtext(NS + 'activityEuLegislative')
        rep['activity_communication'] = act_el.findtext(NS + 'activityRelevantComm')
        rep['activity_high_level_groups'] = act_el.findtext(NS + 'activityHighLevelGroups')
        rep['activity_consult_committee'] = act_el.findtext(NS + 'activityConsultCommittees')
        rep['activity_expert_groups'] = act_el.findtext(NS + 'activityExpertGroups')
        rep['activity_inter_groups'] = act_el.findtext(NS + 'activityInterGroups')
        rep['activity_industry_forums'] = act_el.findtext(NS + 'activityIndustryForums')
        rep['activity_other'] = act_el.findtext(NS + 'activityOther')

    rep['code_of_conduct'] = rep_el.findtext(NS + 'codeOfConduct')
    rep['action_fields'] = []
    for field in rep_el.findall('.//' + NS + 'actionField/' + NS + 'actionField'):
        rep['action_fields'].append(field.text)
    rep['interests'] = []
    for interest in rep_el.findall('.//' + NS + 'interest/' + NS + 'name'):
        rep['interests'].append(interest.text)

    rep['number_of_natural_persons'] = intconv(rep_el.findtext('.//' + NS + 'structure/' + NS
            + 'numberOfNaturalPersons'))
    rep['number_of_organisations'] = intconv(rep_el.findtext('.//' + NS + 'structure/' + NS
            + 'numberOfOrganisations'))

    mem_el = rep_el.find(NS + 'members')
    if mem_el is not None:
        rep['members_100_percent'] = mem_el.findtext(NS + 'members100Percent')
        rep['members_25_percent'] = mem_el.findtext(NS + 'members25Percent')
        rep['members_total'] = mem_el.findtext(NS + 'members')
        rep['members_fte'] = mem_el.findtext(NS + 'membersFTE')
        rep['members_info'] = mem_el.findtext(NS + 'infoMembers')

    #pprint((rep['numberOfNaturalPersons'], rep['numberOfOrganisations']))
    rep['country_of_members'] = []
    el = rep_el.find(NS + 'structure/' + NS + 'countries')
    if el is not None:
        for country in el.findall('.//' + NS + 'country'):
            rep['country_of_members'].append(country.text)

    rep['organisations'] = []
    el = rep_el.find(NS + 'structure/' + NS + 'organisations')
    if el is not None:
        for org_el in el.findall(NS + 'organisation'):
            org = {}
            org['name'] = org_el.findtext(NS + 'name')
            org['number_of_members'] = org_el.findtext(NS + 'numberOfMembers')
            rep['organisations'].append(org)

    fd = {}
    fd_el = rep_el.find(NS + 'financialData')
    if fd_el is not None:
        fd['start_date'] = dateconv(fd_el.findtext(NS + 'startDate'))
        fd['end_date'] = dateconv(fd_el.findtext(NS + 'endDate'))
        fd['eur_sources_procurement'] = intconv(fd_el.findtext(NS + 'eurSourcesProcurement'))
        fd['eur_sources_grants'] = intconv(fd_el.findtext(NS + 'eurSourcesGrants'))
        fi = fd_el.find(NS + 'financialInformation')
        fd['type'] = fi.get(SI + 'type')
        #import ipdb; ipdb.set_trace()
        fd['total_budget'] = intconv(fi.findtext('.//' + NS +
            'total_budget'))
        fd['public_financing_total'] = intconv(fi.findtext('.//' + NS +
            'totalPublicFinancing'))
        fd['public_financing_national'] = intconv(fi.findtext('.//' + NS +
            'nationalSources'))
        fd['public_financing_infranational'] = intconv(fi.findtext('.//' + NS +
            'infranationalSources'))
        cps = fi.find('.//' + NS + 'customisedPublicSources')
        fd['public_customized'] = []
        if cps is not None:
            for src_el in cps.findall(NS + 'customizedSource'):
                src = {}
                src['name'] = src_el.findtext(NS + 'name')
                src['amount'] = intconv(src_el.findtext(NS + 'amount'))
                fd['public_customized'].append(src)
        fd['other_sources_total'] = intconv(fi.findtext('.//' + NS +
            'totalOtherSources'))
        fd['other_sources_donation'] = intconv(fi.findtext('.//' + NS +
            'donation'))
        fd['other_sources_contributions'] = intconv(fi.findtext('.//' + NS +
            'contributions'))

        # TODO customisedOther
        cps = fi.find('.//' + NS + 'customisedOther')
        fd['other_customized'] = []
        if cps is not None:
            for src_el in cps.findall(NS + 'customizedSource'):
                src = {}
                src['name'] = src_el.findtext(NS + 'name')
                src['amount'] = intconv(src_el.findtext(NS + 'amount'))
                fd['other_customized'].append(src)

        fd['direct_rep_costs_min'] = intconv(fi.findtext('.//' + NS +
            'directRepresentationCosts//' + NS + 'min'))
        fd['direct_rep_costs_max'] = intconv(fi.findtext('.//' + NS +
            'directRepresentationCosts//' + NS + 'max'))
        fd['cost_min'] = intconv(fi.findtext('.//' + NS +
            'cost//' + NS + 'min'))
        fd['cost_max'] = intconv(fi.findtext('.//' + NS +
            'cost//' + NS + 'max'))
        fd['cost_absolute'] = intconv(fi.findtext('.//' + NS +
            'cost//' + NS + 'absoluteAmount'))
        fd['turnover_min'] = intconv(fi.findtext('.//' + NS +
            'turnover//' + NS + 'min'))
        fd['turnover_max'] = intconv(fi.findtext('.//' + NS +
            'turnover//' + NS + 'max'))
        fd['turnover_absolute'] = intconv(fi.findtext('.//' + NS +
            'turnover//' + NS + 'absoluteAmount'))
        tb = fi.find(NS + 'turnoverBreakdown')
        fd['turnover_breakdown'] = []
        if tb is not None:
            for range_ in tb.findall(NS + 'customersGroupsInAbsoluteRange'):
                max_ = range_.findtext('.//' + NS + 'max')
                min_ = range_.findtext('.//' + NS + 'min')
                for customer in range_.findall('.//' + NS + 'customer'):
                    fd['turnover_breakdown'].append({
                        'name': customer.findtext(NS + 'name'),
                        'min': intconv(min_),
                        'max': intconv(max_)
                        })
            for range_ in tb.findall(NS + 'customersGroupsInPercentageRange'):
                # FIXME: I hate political compromises going into DB design
                # so directly.
                max_ = range_.findtext('.//' + NS + 'max')
                if max_:
                    max_ = float(max_) / 100.0 * \
                            float(fd['turnover_absolute'] or
                                  fd['turnover_max'] or fd['turnover_min'])
                min_ = range_.findtext('.//' + NS + 'min')
                if min_:
                    min_ = float(min_) / 100.0 * \
                            float(fd['turnover_absolute'] or
                                  fd['turnover_min'] or fd['turnover_max'])
                for customer in range_.findall('.//' + NS + 'customer'):
                    fd['turnover_breakdown'].append({
                        'name': customer.findtext(NS + 'name'),
                        'min': intconv(min_),
                        'max': intconv(max_)
                        })
    # from pprint import pprint
    # pprint(rep)
    rep['fd'] = fd
    return rep


def load_person(person, role, childBase):
    person_ = childBase.copy()
    person_.update(person)
    person_['role'] = role
    person_['name'] = '%s %s %s' % (person['title'] or '',
                                    person['first_name'] or '',
                                    person['last_name'] or '')
    person_['name'] = person_['name'].strip()
    reg_person.upsert(person_, ['representative_etl_id', 'role', 'name'])


def load_finances(financialData, childBase):
    etlId = '%s//%s' % (financialData['start_date'], financialData['end_date'])

    financial_sources = \
        [(s, 'other') for s in financialData.pop("other_customized")] + \
        [(s, 'public') for s in financialData.pop("public_customized")]
    for financial_source, type_ in financial_sources:
        financial_source['type'] = type_
        financial_source['financial_data_etl_id'] = etlId
        financial_source.update(childBase)
        reg_financial_data_custom_source.upsert(financial_source, ['representative_etl_id', 'financial_data_etl_id', 'type', 'name'])

    for turnover in financialData.pop("turnover_breakdown"):
        turnover['financial_data_etl_id'] = etlId
        turnover['name'] = turnover['name'].strip()
        turnover.update(childBase)
        reg_financial_data_turnover.upsert(turnover, ['representative_etl_id', 'financial_data_etl_id', 'name'])

    financialData['etl_id'] = etlId
    financialData.update(childBase)
    reg_financial_data.upsert(financialData, ['representative_etl_id', 'etl_id'])
    #pprint(financialData)


def load_rep(rep):
    rep['first_seen'] = datetime.utcnow()
    rep['last_seen'] = rep['first_seen']
    existing = reg_representative.find_one(identification_code=rep['identification_code'])
    if existing is not None:
        rep['first_seen'] = existing.get('first_seen', rep['first_seen'])
    etlId = rep['etl_id'] = "%s//ALL" % rep['identification_code']
    childBase = {'representative_etl_id': etlId,
                 'representative_update_date': rep['last_update_date']}
    if not rep['original_name']:
        log.error("Unnamed representative: %r", rep)
        return
    load_person(rep.pop('legal_person'), 'legal', childBase)
    load_person(rep.pop('eu_person'), 'eu', childBase)
    for actionField in rep.pop('action_fields'):
        rec = childBase.copy()
        rec['action_field'] = actionField
        reg_action_field.upsert(rec, ['representative_etl_id', 'action_field'])

    for interest in rep.pop('interests'):
        rec = childBase.copy()
        rec['interest'] = interest
        reg_interest.upsert(rec, ['representative_etl_id', 'interest'])

    for countryOfMember in rep.pop('country_of_members'):
        rec = childBase.copy()
        rec['country'] = countryOfMember
        reg_country_of_member.upsert(rec, ['representative_etl_id', 'country'])

    for organisation in rep.pop('organisations'):
        rec = childBase.copy()
        rec.update(organisation)
        rec['name'] = organisation['name'].strip()
        reg_organisation.upsert(rec, ['representative_etl_id', 'name'])

    fd = rep.pop('fd')
    if len(fd.keys()):
        load_finances(fd, childBase)
    rep['name'] = rep['original_name'].strip()
    log.info("Representative: %s", rep['name'])
    reg_representative.upsert(rep, ['etl_id'])


def parse():
    # parser = etree.XMLParser(recover=True)
    res = requests.get(URL, stream=True)
    res.raw.decode_content = True
    for evt, el in etree.iterparse(res.raw, recover=True):
        if evt != 'end' or el.tag != NS + 'interestRepresentative':
            continue
        # print etree.tostring(el, pretty_print=True)
        yield parse_rep(el)
        el.clear()


def extract():
    log.info("Extracting registered interests data...")
    for i, rep in enumerate(parse()):
        load_rep(rep)
        # if i % 100 == 0:
        #     log.info("Extracted: %s...", i)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    extract()
