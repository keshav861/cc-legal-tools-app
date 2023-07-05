# Third-party
from rdflib import Graph, Literal, Namespace, URIRef

# First-party/Local
from legal_tools.models import LegalCode, Tool


def generate_rdf_triples(unit, version, jurisdiction_code=None):
    # Retrieving license data from the database based on the arguments.
    if jurisdiction_code:
        license_data = Tool.objects.filter(
            unit=unit, version=version, jurisdiction_code=jurisdiction_code
        ).first()
    else:
        license_data = Tool.objects.filter(unit=unit, version=version).first()

    # The relevant namespaces for RDF elements
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    CC = Namespace("https://creativecommons.org/ns#")
    DCTYPES = Namespace("http://purl.org/dc/dcmitype/")
    DCT = Namespace("http://purl.org/dc/terms/")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    DC = Namespace("http://purl.org/dc/elements/1.1/")

    g = Graph()

    # Bind namespaces
    g.bind("cc", CC)
    g.bind("dc", DC)
    g.bind("dct", DCT)
    g.bind("dctypes", DCTYPES)
    g.bind("foaf", FOAF)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)

    # license URI
    license_uri = URIRef(license_data.base_url)

    g.add((license_uri, CC.License, license_uri))
    g.add((license_uri, DC.identifier, Literal(f"{unit}")))
    g.add((license_uri, CC.licenseVersion, Literal(f"{version}")))
    g.add((license_uri, FOAF.maker, URIRef("https://creativecommons.org/")))

    """g.add(
        (
            license_uri,
            DCT.description,
            Literal(" NEED SUGGESTIONS ON WHAT TO PUT HERE."),
        )
    )"""

    if jurisdiction_code:
        code = jurisdiction_code
        g.add(
            (
                license_uri,
                CC.jurisdiction,
                URIRef("https://creativecommons.org/international/" + code),
            )
        )

    # Extracted the corresponding id of the Tool from LegalCode and then
    # created CC.legalcode using 'legal_code_url' property of LegalCode.
    legal_code_ids = license_data.legal_codes.values_list("id", flat=True)
    for legal_code_id in legal_code_ids:
        legal_codes = LegalCode.objects.get(id=legal_code_id)
        legal_code_url = legal_codes.legal_code_url
        g.add(
            (
                license_uri,
                CC.legalcode,
                URIRef(license_data.creator_url + legal_code_url),
            )
        )

    # Adding properties
    # Permits
    if license_data.permits_derivative_works:
        g.add((license_uri, CC.permits, CC.DerivativeWorks))
    if license_data.permits_distribution:
        g.add((license_uri, CC.permits, CC.Distribution))
    if license_data.permits_reproduction:
        g.add((license_uri, CC.permits, CC.Reproduction))
    if license_data.permits_sharing:
        g.add((license_uri, CC.permits, CC.Sharing))

    # Requires
    if license_data.requires_attribution:
        g.add((license_uri, CC.requires, CC.Attribution))
    if license_data.requires_notice:
        g.add((license_uri, CC.requires, CC.Notice))
    if license_data.requires_share_alike:
        g.add((license_uri, CC.requires, CC.ShareAlike))
    if license_data.requires_source_code:
        g.add((license_uri, CC.requires, CC.SourceCode))

    # Prohibits
    if license_data.prohibits_commercial_use:
        g.add((license_uri, CC.prohibits, CC.CommercialUse))
    if license_data.prohibits_high_income_nation_use:
        g.add((license_uri, CC.prohibits, CC.HighIncomeNationUse))

    return g
