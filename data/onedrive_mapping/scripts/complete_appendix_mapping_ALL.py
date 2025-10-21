#!/usr/bin/env python3
"""
Complete appendix mapping with FIXED nested folder handling.
"""

import csv
import os
import re

# Paths
ONEDRIVE_BASE = "/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation"
APPENDICES_DIR = os.path.join(ONEDRIVE_BASE, "TheBRIDGE - Montlake - Contract Documents/Appendices")
CSV_PATH = "/Users/z/Desktop/git/montlake-closeout/data/documents_tracker.csv"
OUTPUT_CSV = "/Users/z/Desktop/git/montlake-closeout/data/documents_tracker_COMPLETE.csv"
REPORT_TXT = "/Users/z/Desktop/git/montlake-closeout/data/complete_mapping_report.txt"

# Complete appendix mapping extracted from the PDF
APPENDIX_DATA = {
    # A - Project Files
    ('A - Project Files', 'A1'): 'Appendices List',
    ('A - Project Files', 'A2'): 'Electronic Files',
    ('A - Project Files', 'A3'): 'Photos',
    ('A - Project Files', 'A4.1'): 'SR520 Differential Level Report',
    ('A - Project Files', 'A4.2'): 'SR520 GPS Control Network',

    # A-B - As-Built Plans and Construction
    ('A-B - As-Built Plans and Construction', 'A-B1.B'): 'West Approach Bridge',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.1'): 'Volume 01',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.2'): 'Volume 02',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.3'): 'Volume 03',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.4'): 'Volume 04',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.5'): 'Volume 05',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.6'): 'Volume 06',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.7'): 'Volume 07',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.8'): 'Volume 08',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.9'): 'Volume 09',
    ('A-B - As-Built Plans and Construction', 'A-B1.E.10'): 'Volume 10',
    ('A-B - As-Built Plans and Construction', 'A-B1.F.1'): 'WABN RFI Log',
    ('A-B - As-Built Plans and Construction', 'A-B1.F.2'): 'WABN RFI Questions',
    ('A-B - As-Built Plans and Construction', 'A-B1.G.1'): 'WABN DCRs & IDRs Part 1',
    ('A-B - As-Built Plans and Construction', 'A-B1.G.2'): 'WABN DCRs & IDRs Part 2',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.1'): 'As-Built Plans Volume 01',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.2'): 'As-Built Plans Volume 02',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.3'): 'As-Built Plans Volume 03',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.4'): 'As-Built Plans Volume 04',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.5'): 'As-Built Plans Volume 05',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.6'): 'As-Built Plans Volume 06',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.7'): 'As-Built Plans Volume 06a',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.8'): 'As-Built Plans Volume 06b',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.9'): 'As-Built Plans Volume 07',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.10'): 'As-Built Plans Volume 07a',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.11'): 'As-Built Plans Volume 08',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.12'): 'As-Built Plans Volume 09',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.13'): 'As-Built Plans Volume 10',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.14'): 'As-Built Plans Volume 11',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.15'): 'As-Built Plans Volume 12',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.16'): 'As-Built Plans Volume 13',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.17'): 'As-Built Plans Volume 14a',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.18'): 'As-Built Plans Volume 14b',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.19'): 'As-Built Plans Volume 14c',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.20'): 'As-Built Plans Volume 14d',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.21'): 'As-Built Plans Volume 15',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.22'): 'As-Built Plans Volume 15a',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.23'): 'As-Built Plans Volume 16',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.24'): 'As-Built Plans Volume 17',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.25'): 'As-Built Plans Volume 18',
    ('A-B - As-Built Plans and Construction', 'A-B2.A.26'): 'As-Built Plans Volume 19',

    # B - Specifications
    ('B - Specifications', 'B1'): 'Amendments to the Standard Specifications',
    ('B - Specifications', 'B14'): 'City of Seattle Standard Specifications',
    ('B - Specifications', 'B15'): 'King County Metro Electrical',
    ('B - Specifications', 'B16'): 'Steel Escalation Cost Adjustment',

    # C - Commitments List
    ('C - Commitments List', 'C1'): 'Environmental Commitments List',

    # D - Manuals
    ('D - Manuals', 'D1'): 'Bridge Design Manual',
    ('D - Manuals', 'D2'): 'Construction Manual',
    ('D - Manuals', 'D3'): 'Design Manual',
    ('D - Manuals', 'D4'): 'Environmental Manual',
    ('D - Manuals', 'D5'): 'Geotechnical Design Manual',
    ('D - Manuals', 'D6'): 'Highway Runoff Manual',
    ('D - Manuals', 'D7'): 'Hydraulics Manual',
    ('D - Manuals', 'D8'): 'Local Agency Guidelines',
    ('D - Manuals', 'D9'): 'Maintenance Manual',
    ('D - Manuals', 'D10'): 'Materials Manual',
    ('D - Manuals', 'D11'): 'Pavement Surface Condition',
    ('D - Manuals', 'D12'): 'Plans Preparation Manual',
    ('D - Manuals', 'D13'): 'Organizational Conflicts of Interest Manual',
    ('D - Manuals', 'D14'): 'Right of Way Manual',
    ('D - Manuals', 'D15'): 'Roadside Classification Plan',
    ('D - Manuals', 'D16'): 'Roadside Manual',
    ('D - Manuals', 'D17'): 'Standard Plans',
    ('D - Manuals', 'D18'): 'Electronic Engineering Data Standards',
    ('D - Manuals', 'D19'): 'Traffic Manual',
    ('D - Manuals', 'D20'): 'Utilities Accommodation Policy',
    ('D - Manuals', 'D21'): 'Utilities Manual',
    ('D - Manuals', 'D22'): 'Communications Manual',
    ('D - Manuals', 'D23'): 'Highway Surveying Manual',
    ('D - Manuals', 'D24'): 'Temporary Erosion',
    ('D - Manuals', 'D25'): 'WA MUTCD Modifications',
    ('D - Manuals', 'D26'): 'Sign Fabrication Manual',
    ('D - Manuals', 'D27'): 'Work Zone Traffic Control Guidelines',
    ('D - Manuals', 'D28'): 'FHWA MUTCD',
    ('D - Manuals', 'D29'): 'Bridge Inspection Manual',
    ('D - Manuals', 'D30'): 'Seattle ROWORR',
    ('D - Manuals', 'D31'): 'Seattle Standard Plans 2017',
    ('D - Manuals', 'D33'): 'NWR HOV Design Guide',
    ('D - Manuals', 'D34.A'): 'Wide Flange Deck Bulb Tee',
    ('D - Manuals', 'D34.B'): 'Bridge Deck Protection System',
    ('D - Manuals', 'D34.C'): 'Bridge Design Minimum Requirements',
    ('D - Manuals', 'D34.D'): 'Scour Requirements',
    ('D - Manuals', 'D34.F'): 'Bridge Paving Projects',
    ('D - Manuals', 'D34.G'): 'Positive Moment Strand Extension',
    ('D - Manuals', 'D34.H'): 'Pre-Bent Stirrups',
    ('D - Manuals', 'D35'): 'Seattle ROW Improvements Manual',
    ('D - Manuals', 'D36'): 'Seattle Traffic Control Manual',
    ('D - Manuals', 'D37'): 'FHWA Traffic Control Systems Handbook',
    ('D - Manuals', 'D38'): 'SPU Design Standards',
    ('D - Manuals', 'D39'): 'FHWA Flexibility In Highway Design',
    ('D - Manuals', 'D40'): 'ET 31 ET Plus Guardrail Terminal Memo',
    ('D - Manuals', 'D42'): 'NWR Area 5',
    ('D - Manuals', 'D43'): 'DOE Sewage Works Design Criteria',
    ('D - Manuals', 'D44'): 'Seattle City Light Stock Catalog',
    ('D - Manuals', 'D46'): 'King County Road Design',
    ('D - Manuals', 'D47'): 'DOH Water System Manual',
    ('D - Manuals', 'D48.A'): 'SDOT Companion Ramp',
    ('D - Manuals', 'D48.B'): 'SDOT ADA Curb Ramp Assessment',
    ('D - Manuals', 'D48.C'): 'SDOT Curb Ramp Flares',
    ('D - Manuals', 'D48.D'): 'SDOT Curb Ramp Construction Tolerances',
    ('D - Manuals', 'D48.E'): 'SDOT Curb Ramps T-Intersections',
    ('D - Manuals', 'D48.F'): 'SDOT MEF Documentation Curb Ramp',
    ('D - Manuals', 'D48.G'): 'SDOT APS Installation Requirements',
    ('D - Manuals', 'D49'): 'Seattle CAD Manual',

    # E - Environmental (38 appendices from PDF - huge category!)
    ('E - Environmental', 'E1.A'): 'Record of Decision',
    ('E - Environmental', 'E1.B'): 'Final Environmental Impact Statement',
    ('E - Environmental', 'E1.C.1'): 'SEPA Public Place Designation',
    ('E - Environmental', 'E1.C.2'): 'SEPA Public Place Authorization',
    ('E - Environmental', 'E1.E'): 'SEPA Floating Bridge',
    ('E - Environmental', 'E1.G'): 'Kenmore Yard',
    ('E - Environmental', 'E1.H'): 'Floating Bridge',
    ('E - Environmental', 'E1.J'): 'Kenmore Yard Update',
    ('E - Environmental', 'E1.K'): 'FB&L Final Design Features',
    ('E - Environmental', 'E1.L'): 'Westside Staging Area',
    ('E - Environmental', 'E1.M'): 'WCB',
    ('E - Environmental', 'E1.N'): 'Floating Bridge Demolition',
    ('E - Environmental', 'E1.O'): 'WABS Montlake Lid',
    ('E - Environmental', 'E1.P'): 'Pontoon Tacoma Blair',
    ('E - Environmental', 'E1.Q'): 'FB&L Construction Changes',
    ('E - Environmental', 'E1.R'): 'Kenmore Yard Update',
    ('E - Environmental', 'E1.S'): 'Eastside Staging Area',
    ('E - Environmental', 'E1.T'): 'Geotechnical Investigations',
    ('E - Environmental', 'E1.U'): 'Construction Truck Trips',
    ('E - Environmental', 'E1.V'): 'FB&L Final Design',
    ('E - Environmental', 'E1.W'): 'Additional Moorage Buoys',
    ('E - Environmental', 'E1.X'): 'Rescind Stormwater Changes',
    ('E - Environmental', 'E1.Y'): 'PATON Buoy Strings',
    ('E - Environmental', 'E1.Z'): 'Channel Marker Repair',
    ('E - Environmental', 'E1.AA'): 'Montlake Construction Limits',
    ('E - Environmental', 'E1.BB'): 'Wetland Mitigation Addendum',
    ('E - Environmental', 'E1.CC'): 'Pontoon Repairs Vigor',
    ('E - Environmental', 'E1.DD'): 'Pontoon Tacoma Terminal 7',
    ('E - Environmental', 'E1.FF'): 'Pontoon Repairs Coffer Cell',
    ('E - Environmental', 'E1.GG'): 'WABN',
    ('E - Environmental', 'E1.HH'): 'WABN Foster Island Refinements',
    ('E - Environmental', 'E1.II'): 'WABN Foster Island Design',
    ('E - Environmental', 'E1.JJ'): 'Tolling Equipment',
    ('E - Environmental', 'E1.KK'): 'Eastside Haul Routes',
    ('E - Environmental', 'E1.LL'): 'Geotechnical Investigation',
    ('E - Environmental', 'E1.MM'): 'Section 106 Amendment',
    ('E - Environmental', 'E1.NN'): 'Tolling Equipment Installation',
    ('E - Environmental', 'E1.OO'): 'Montlake Market Closure',
    ('E - Environmental', 'E2'): 'Environmental Project Description',
    ('E - Environmental', 'E3.A'): 'Final Aquatic Mitigation Plan',
    ('E - Environmental', 'E3.B'): 'Final Wetland Mitigation Report',
    ('E - Environmental', 'E3.C'): 'Aquatic Wetland Mitigation Addendum 5',
    ('E - Environmental', 'E3.D'): 'Permit Plans - Corps',
    ('E - Environmental', 'E3.E'): 'Permit Plans - Seattle Shoreline',
    ('E - Environmental', 'E3.F'): 'Permit Plans - Coast Guard',
    ('E - Environmental', 'E3.G'): 'Permit Plans - WDFW Ecology',
    ('E - Environmental', 'E3.H'): 'Wetland Mitigation Addendum 7',
    ('E - Environmental', 'E4.A'): 'Biological Assessment',
    ('E - Environmental', 'E4.B'): 'West Approach ESA Reinitiation',
    ('E - Environmental', 'E4.C'): 'Bubble Curtain Plans',
    ('E - Environmental', 'E4.D'): 'Pile Driving Flow Chart',
    ('E - Environmental', 'E5.A'): 'Section 106 Programmatic Agreement',
    ('E - Environmental', 'E5.B'): 'Section 106 Agreement Amendment 1',
    ('E - Environmental', 'E6'): 'Unanticipated Discovery Plan',
    ('E - Environmental', 'E7'): 'Historic Properties Archaeologically Sensitive Areas',
    ('E - Environmental', 'E9'): 'Foster Island Treatment Plan',
    ('E - Environmental', 'E10'): 'Community Construction Management Plan',
    ('E - Environmental', 'E11'): 'Tree Vegetation Management Protection Plan',
    ('E - Environmental', 'E12'): 'Neighborhood Traffic Management Plan',
    ('E - Environmental', 'E14'): 'TESC Plan Narrative Template',
    ('E - Environmental', 'E15'): 'Sustainability Performance Relationships',
    ('E - Environmental', 'E18'): 'Fish Exclusion Protocols Standards',
    ('E - Environmental', 'E19'): 'Recycled Concrete Aggregate PCCP',
    ('E - Environmental', 'E20'): 'DOE Petroleum Remediation Guidance',
    ('E - Environmental', 'E21'): 'Hazardous Materials Baseline Report',
    ('E - Environmental', 'E22'): 'MTCA Exceedances WABN Geotechnical',
    ('E - Environmental', 'E23'): 'Phase I ESA Montlake Gas Station',
    ('E - Environmental', 'E24'): 'WABN Construction Testing Results',
    ('E - Environmental', 'E25'): 'WABN Gas Monitoring Report 5',
    ('E - Environmental', 'E26'): 'Environmental Constraints Plan',
    ('E - Environmental', 'E27'): 'Phase II ESA Eastbound Off-Ramp',
    ('E - Environmental', 'E28'): 'Hazardous Materials Report Addendum',
    ('E - Environmental', 'E29'): 'Phase II ESA - Exterior',
    ('E - Environmental', 'E31'): 'WABN Landfill Gas Monitoring Logs',
    ('E - Environmental', 'E32.A'): 'Construction Noise Variance Decision',
    ('E - Environmental', 'E32.B.1'): 'Noise Variance Application',
    ('E - Environmental', 'E32.B.2'): 'Seattle Noise Variance Attachment',
    ('E - Environmental', 'E32.B.3'): 'Noise Variance Notification Map',
    ('E - Environmental', 'E33'): 'Seattle Olmsted Park Furniture Standards',
    ('E - Environmental', 'E34.A'): 'Bridge 513-10 Good Faith Survey',
    ('E - Environmental', 'E34.B'): 'Bridge 520 3 and 3E-N Survey',
    ('E - Environmental', 'E34.C'): 'Bridge 520-5 and 5A Survey',
    ('E - Environmental', 'E34.D'): 'Bridges 520 6 7.5N 7.5 7.7S Survey',
    ('E - Environmental', 'E34.E'): 'Bridge 520 6A and 6N-E Survey',
    ('E - Environmental', 'E35'): 'FB&L Demo Test Results',
    ('E - Environmental', 'E36'): 'Phase II ESA East Montlake Place',
    ('E - Environmental', 'E36.A'): 'Analytical Data Lab 1805-191B',
    ('E - Environmental', 'E37'): 'West Approach Salmonid Migration Zone',
    ('E - Environmental', 'E38.A'): 'NPDES Construction Stormwater Permit',
    ('E - Environmental', 'E38.B'): 'Administrative Order',
    ('E - Environmental', 'E38.C'): 'Administrative Order Amendment',

    # F - Forms (8 appendices from PDF)
    ('F - Forms', 'F1'): 'Site Inspection Form',
    ('F - Forms', 'F2'): 'Contract Bond Form',
    ('F - Forms', 'F3'): 'Report of Survey Mark Form',
    ('F - Forms', 'F4'): 'Chemical Treatment Form',
    ('F - Forms', 'F5.A'): 'DRB Administrative Procedures',
    ('F - Forms', 'F5.B'): 'DRB State Member Scope',
    ('F - Forms', 'F6'): 'Manufacturer Certificate Compliance Form',
    ('F - Forms', 'F7.A'): 'Traffic Control Daily Report Summary',
    ('F - Forms', 'F7.B'): 'Traffic Control Daily Log',
    ('F - Forms', 'F8'): 'ROM Sample',

    # G - Geotechnical (25 appendices from PDF)
    ('G - Geotechnical', 'G1'): 'Geotechnical Baseline Report',
    ('G - Geotechnical', 'G2'): 'Geotechnical Data Report',
    ('G - Geotechnical', 'G3'): 'Earthquake Ground Motions Seismic Design',
    ('G - Geotechnical', 'G4'): 'Seismic Design Technical Memorandum',
    ('G - Geotechnical', 'G5'): 'Supplemental Preliminary Engineering Memo',
    ('G - Geotechnical', 'G6'): 'West Approach Geologic Characterization',
    ('G - Geotechnical', 'G7'): 'West Approach Geologic Characterization Addendum',
    ('G - Geotechnical', 'G8'): 'Summary Previous Construction Activities',
    ('G - Geotechnical', 'G9'): 'Revised Seismic Ground Motions',
    ('G - Geotechnical', 'G10'): 'WABN Geotechnical Report Addendum',
    ('G - Geotechnical', 'G11'): 'Westside Stormwater Facilities Memo',
    ('G - Geotechnical', 'G12'): 'Westside Montlake Bike-Pedestrian Facilities Memo',
    ('G - Geotechnical', 'G13'): 'Westside Montlake Lid Land Bridge Memo',
    ('G - Geotechnical', 'G14'): 'WABN Geotechnical Engineering Report',
    ('G - Geotechnical', 'G14.A'): 'WABN Geotechnical Attach F App B',
    ('G - Geotechnical', 'G14.B'): 'WABN Geotechnical Attach F App D',
    ('G - Geotechnical', 'G14.C'): 'WABN Geotechnical Attach F App E',
    ('G - Geotechnical', 'G15'): 'WAB South Frame 5 Soil-Structure Modeling',
    ('G - Geotechnical', 'G16'): 'Test Pile Geotechnical Data Report',
    ('G - Geotechnical', 'G17'): 'Existing Geotechnical Data Report',
    ('G - Geotechnical', 'G18'): 'Limitations Geotechnical Documents',
    ('G - Geotechnical', 'G19'): 'Geotechnical Report WCB',
    ('G - Geotechnical', 'G20'): 'Geotechnical Data Report Addendum',
    ('G - Geotechnical', 'G21.A'): 'West Approach Bridge Pile Driving Info',
    ('G - Geotechnical', 'G21.B'): 'Union Bay Bridge Pile Driving Info',
    ('G - Geotechnical', 'G22'): 'Montlake WABN Condition Survey',
    ('G - Geotechnical', 'G23.A'): 'WABN 24th Ave Field Reports',
    ('G - Geotechnical', 'G23.B'): 'Change Order 44',
    ('G - Geotechnical', 'G23.C'): 'Construction Photos',
    ('G - Geotechnical', 'G23.D'): 'WABN 24th Ave Shoring Plan',
    ('G - Geotechnical', 'G24'): 'U-Link Moment-Thrust Capacity Calculations',
    ('G - Geotechnical', 'G25'): 'Seattle Yacht Club Bulkhead Inspection',

    # H - Hydraulics (16 appendices from PDF)
    ('H - Hydraulics', 'H1'): 'Conceptual Supplemental Hydraulic Report',
    ('H - Hydraulics', 'H2'): 'Hydraulic Report Template',
    ('H - Hydraulics', 'H3'): 'Hydraulic Report WABN',
    ('H - Hydraulics', 'H4'): 'Final As-Built Hydraulic Report FB&L',
    ('H - Hydraulics', 'H5'): 'WABN Supplemental Hydraulic Report',
    ('H - Hydraulics', 'H6'): 'Program Level Hydraulic Report',
    ('H - Hydraulics', 'H9'): 'Seattle Stormwater Manual',
    ('H - Hydraulics', 'H12'): 'Drainage Maintenance Manual Plan Sheets',
    ('H - Hydraulics', 'H13'): 'ACPA Concrete Pipe Design Manual',
    ('H - Hydraulics', 'H15'): 'DIPRA Ductile Iron Pipe Supports',
    ('H - Hydraulics', 'H16'): 'SPU Client Assistance Memo 1180',

    # I - Illumination, Electrical & ITS (17 appendices from PDF)
    ('I - Illumination, Electrical & ITS', 'I1'): 'NWR Electrical Design Practices',
    ('I - Illumination, Electrical & ITS', 'I2'): 'NWR Illumination Signal Details',
    ('I - Illumination, Electrical & ITS', 'I3'): 'NWR ITS Details',
    ('I - Illumination, Electrical & ITS', 'I4'): 'Power System Design',
    ('I - Illumination, Electrical & ITS', 'I5'): 'Illumination Design Supplement',
    ('I - Illumination, Electrical & ITS', 'I6'): 'AGi32 Basics WSDOT Highway Lighting',
    ('I - Illumination, Electrical & ITS', 'I7'): 'Advanced Inspection Illumination Signal Training',
    ('I - Illumination, Electrical & ITS', 'I8'): 'NWR ITS Design Requirements',
    ('I - Illumination, Electrical & ITS', 'I10'): 'Seattle Electrical Code',
    ('I - Illumination, Electrical & ITS', 'I12'): 'Seattle City Light Construction Standards',
    ('I - Illumination, Electrical & ITS', 'I13'): 'Seattle City Light Service Connection Requirements',
    ('I - Illumination, Electrical & ITS', 'I14'): 'Seattle ROW Lighting Design Guidelines',
    ('I - Illumination, Electrical & ITS', 'I15'): 'Seattle City Light Material Standards',
    ('I - Illumination, Electrical & ITS', 'I16'): 'Design of Outdoor Lighting',
    ('I - Illumination, Electrical & ITS', 'I19'): 'SPR Electrical System Design Standard',
    ('I - Illumination, Electrical & ITS', 'I22'): 'Corridor Fiber Optic Communication Plan',
    ('I - Illumination, Electrical & ITS', 'I23'): 'Seattle City Light Service Standards',

    # J - Pavement
    ('J - Pavement', 'J1'): 'Pavement Design Report',
    ('J - Pavement', 'J2'): 'WABN Pavement Design Report',
    ('J - Pavement', 'J3'): 'Pavement Policy',
    ('J - Pavement', 'J4'): 'Pavement Project Specifications',

    # K - Prevailing Wages (3 appendices from PDF)
    ('K - Prevailing Wages', 'K2.A'): 'WA Prevailing Wages King County',
    ('K - Prevailing Wages', 'K2.B'): 'Supplemental to Wages',
    ('K - Prevailing Wages', 'K2.C'): 'Benefit Code Key',

    # L - Landscape and Urban Design (14 appendices from PDF)
    ('L - Landscape and Urban Design', 'L1'): 'Urban Design Exhibits',
    ('L - Landscape and Urban Design', 'L2'): 'Seattle Design Commission Report',
    ('L - Landscape and Urban Design', 'L3'): 'American Standard Nursery Stock',
    ('L - Landscape and Urban Design', 'L4'): 'Landscape Maintenance Water Use Form',
    ('L - Landscape and Urban Design', 'L5'): 'Seattle Pedestrian Wayfinding Symbols',
    ('L - Landscape and Urban Design', 'L6'): 'Seattle Parks Technical Specifications',
    ('L - Landscape and Urban Design', 'L7'): 'Seattle Parks Standard Details Plans',
    ('L - Landscape and Urban Design', 'L8'): 'Seattle Parks Maintenance Utility Impact',
    ('L - Landscape and Urban Design', 'L9'): 'Seattle Bicycle Guide Sign Practice',
    ('L - Landscape and Urban Design', 'L10'): 'UW Irrigation Design Guide',
    ('L - Landscape and Urban Design', 'L11'): 'Seattle Street Tree Manual',
    ('L - Landscape and Urban Design', 'L12'): 'GCB 1895',
    ('L - Landscape and Urban Design', 'L13'): 'Seattle Tree Replacement Executive Order',
    ('L - Landscape and Urban Design', 'L14'): 'UW Technical Specifications',

    # M - Conceptual Plans (22 appendices from PDF)
    ('M - Conceptual Plans', 'M1'): 'Conceptual Plans',
    ('M - Conceptual Plans', 'M7'): 'WAB Pier Layouts Clearance Requirements',
    ('M - Conceptual Plans', 'M8'): 'Existing Bridge Demolition Plans',
    ('M - Conceptual Plans', 'M9'): 'Existing Walls to Remain Plan',
    ('M - Conceptual Plans', 'M10'): 'Work Access Pile Restriction Plan',
    ('M - Conceptual Plans', 'M11'): 'Future Four-Lane Plus Two HCT',
    ('M - Conceptual Plans', 'M12'): 'Future Six-Lane Plus Two HCT',
    ('M - Conceptual Plans', 'M14'): 'West Approach Architectural Standards',
    ('M - Conceptual Plans', 'M15'): 'Sign Structure Connection Details',
    ('M - Conceptual Plans', 'M16'): 'Permanent Barrier Modification Plan',
    ('M - Conceptual Plans', 'M18'): 'Bascule Bridge Conceptual Plans',
    ('M - Conceptual Plans', 'M19'): 'Portage Bay Bridge Conceptual Plans',
    ('M - Conceptual Plans', 'M21'): 'Noxious Weed Infestation Map',
    ('M - Conceptual Plans', 'M22'): 'North Transit Facility Diagram',

    # N - Local Agency Agreements (4 appendices from PDF)
    ('N - Local Agency Agreements', 'N2'): 'Maintenance and Operation Areas',
    ('N - Local Agency Agreements', 'N3'): 'Seattle Design-Build Agreement',
    ('N - Local Agency Agreements', 'N4'): 'Street Use Permit General Conditions',
    ('N - Local Agency Agreements', 'N4.A'): 'Street Use Permit Special Conditions',

    # O - Design Documentation (40+ appendices from PDF)
    ('O - Design Documentation', 'O1'): 'Design Documentation Package Checklist',
    ('O - Design Documentation', 'O2'): 'Project File Checklist',
    ('O - Design Documentation', 'O3'): 'Design Analysis Decision Template',
    ('O - Design Documentation', 'O5.A'): 'PIF 1 Mageba Expansion Joints',
    ('O - Design Documentation', 'O5.B'): 'PIF 1 Appendices Combined',
    ('O - Design Documentation', 'O6'): 'Design Parameter Template',
    ('O - Design Documentation', 'O7'): 'Design Approval Package',
    ('O - Design Documentation', 'O8.A'): 'Design Analysis 1',
    ('O - Design Documentation', 'O8.B'): 'Design Analysis 2',
    ('O - Design Documentation', 'O8.C'): 'Design Analysis 3 Revisions 1',
    ('O - Design Documentation', 'O8.D'): 'Design Analysis 4',
    ('O - Design Documentation', 'O8.E'): 'Design Analysis 5 Revisions 1',
    ('O - Design Documentation', 'O8.F'): 'Design Analysis 6',
    ('O - Design Documentation', 'O8.G'): 'Design Analysis 7',
    ('O - Design Documentation', 'O8.H'): 'Design Analysis 8',
    ('O - Design Documentation', 'O8.I'): 'Design Analysis 9',
    ('O - Design Documentation', 'O8.J'): 'Design Analysis 10',
    ('O - Design Documentation', 'O8.L'): 'Design Analysis 12',
    ('O - Design Documentation', 'O8.M'): 'Design Analysis 13',
    ('O - Design Documentation', 'O9.A'): 'Proprietary Items Memo 1',
    ('O - Design Documentation', 'O9.B'): 'Proprietary Items Memo 1 Appendices',
    ('O - Design Documentation', 'O9.C'): 'Proprietary Items Memo 2',
    ('O - Design Documentation', 'O9.D'): 'Proprietary Items Memo 2 Appendices',
    ('O - Design Documentation', 'O9.E'): 'Proprietary Items Memo 3',
    ('O - Design Documentation', 'O9.F'): 'Proprietary Items Memo 3 Appendices',
    ('O - Design Documentation', 'O9.G'): 'Proprietary Items Memo 4',
    ('O - Design Documentation', 'O9.H'): 'Proprietary Items Memo 4 Appendices',
    ('O - Design Documentation', 'O9.I'): 'Proprietary Items Memo 5',
    ('O - Design Documentation', 'O9.J'): 'Proprietary Items Memo 5 Appendices',
    ('O - Design Documentation', 'O10'): 'NWR Channelization Plan Checklist',
    ('O - Design Documentation', 'O11.A'): 'Design Decision WB Off-Ramp Montlake',
    ('O - Design Documentation', 'O11.B'): 'Design Decision WB Off-Ramp 24th Ave',
    ('O - Design Documentation', 'O11.C'): 'Design Decision WB Lane Reduction',
    ('O - Design Documentation', 'O11.D'): 'Design Decision 24th Ave E',
    ('O - Design Documentation', 'O11.E'): 'Design Decision Direct Access Connector',
    ('O - Design Documentation', 'O11.F'): 'Design Decision E Lake Washington Blvd',
    ('O - Design Documentation', 'O12'): 'MEF Template',
    ('O - Design Documentation', 'O13'): 'MEF Worksheet',
    ('O - Design Documentation', 'O14.A'): 'State Furnished Signal Equipment Memo',
    ('O - Design Documentation', 'O14.B'): 'State Furnished Signal Equipment Attachment',
    ('O - Design Documentation', 'O15'): 'Contract File Index',

    # P - Permits and Approvals (35+ appendices from PDF)
    ('P - Permits and Approvals', 'P1'): 'Corps Permit',
    ('P - Permits and Approvals', 'P1.A'): 'Water Quality Certification',
    ('P - Permits and Approvals', 'P2.A'): 'USCG General Bridge Permit',
    ('P - Permits and Approvals', 'P2.B'): 'USCG Bridge Permit Amendment',
    ('P - Permits and Approvals', 'P3'): 'Coastal Zone Management Consistency',
    ('P - Permits and Approvals', 'P4.A'): 'Water Quality Certification Order 9011',
    ('P - Permits and Approvals', 'P4.B'): 'Water Quality Cert Amendment 1',
    ('P - Permits and Approvals', 'P4.C'): 'Water Quality Cert Amendment 2',
    ('P - Permits and Approvals', 'P4.D'): 'Water Quality Cert Amendment 3',
    ('P - Permits and Approvals', 'P4.E'): 'Water Quality Cert Amendment 4',
    ('P - Permits and Approvals', 'P4.F'): 'Water Quality Cert Amendment 5',
    ('P - Permits and Approvals', 'P4.G'): 'Water Quality Cert Amendment 6',
    ('P - Permits and Approvals', 'P4.H'): 'Corps Permit Modification',
    ('P - Permits and Approvals', 'P5'): 'WDFW Hydraulic Project Approval',
    ('P - Permits and Approvals', 'P6.A'): 'West Approach Shoreline Development Permit',
    ('P - Permits and Approvals', 'P6.B'): 'Seattle Master Use Permit WAB',
    ('P - Permits and Approvals', 'P7.A'): 'NMFS Biological Opinion',
    ('P - Permits and Approvals', 'P7.B'): 'NMFS R001',
    ('P - Permits and Approvals', 'P7.C'): 'NMFS R002',
    ('P - Permits and Approvals', 'P7.D'): 'NMFS R003',
    ('P - Permits and Approvals', 'P7.E'): 'NMFS R004',
    ('P - Permits and Approvals', 'P7.F'): 'NMFS R005',
    ('P - Permits and Approvals', 'P7.G'): 'NMFS R006',
    ('P - Permits and Approvals', 'P7.H'): 'USFWS Biological Opinion',
    ('P - Permits and Approvals', 'P7.I'): 'USFWS R001',
    ('P - Permits and Approvals', 'P7.J'): 'USFWS R002',
    ('P - Permits and Approvals', 'P7.K'): 'USFWS R003',
    ('P - Permits and Approvals', 'P7.L'): 'USFWS R004',
    ('P - Permits and Approvals', 'P7.M'): 'USFWS R005',
    ('P - Permits and Approvals', 'P7.N'): 'USFWS R006',
    ('P - Permits and Approvals', 'P7.O'): 'USFWS R007',

    # R - Right-of-Way (30+ appendices from PDF)
    ('R - Right-of-Way', 'R1'): 'Illegal Encampments ROW',
    ('R - Right-of-Way', 'R2.A'): 'SR 520 SR 5 to Evergreen Point Bridge',
    ('R - Right-of-Way', 'R2.B'): 'SR 520 Evergreen Point Bridge',
    ('R - Right-of-Way', 'R2.C'): 'SR 520 Montlake to Arboretum ROW',
    ('R - Right-of-Way', 'R2.D'): 'SR 513 SR 520 to NE 45th ROW',
    ('R - Right-of-Way', 'R2.F'): 'SR 520 I-5 to Montlake ROW',
    ('R - Right-of-Way', 'R3'): 'Grant W-04299',
    ('R - Right-of-Way', 'R5.A'): 'WSDOT Sound Transit Airspace Lease',
    ('R - Right-of-Way', 'R5.B'): 'Old Canal Reserve Deed',
    ('R - Right-of-Way', 'R5.C'): 'Sound Transit Easement Old Canal Reserve',
    ('R - Right-of-Way', 'R5.D'): 'Sound Transit Easement Montlake',
    ('R - Right-of-Way', 'R5.E'): 'Sound Transit Light Rail Accommodation',
    ('R - Right-of-Way', 'R5.F'): 'SR 520 Montlake Vicinity Deed',
    ('R - Right-of-Way', 'R5.G'): 'Arboretum E Montlake Park Deed',
    ('R - Right-of-Way', 'R5.H'): 'Aquatic Easement',
    ('R - Right-of-Way', 'R5.I'): 'Aquatic Easement Amendment',
    ('R - Right-of-Way', 'R5.J'): 'McCurdy E Montlake Park Deed',
    ('R - Right-of-Way', 'R5.K'): 'McCurdy E Montlake Park Deed',
    ('R - Right-of-Way', 'R5.L'): 'McCurdy Park Deed',
    ('R - Right-of-Way', 'R5.M'): 'McCurdy E Montlake Park Deed',
    ('R - Right-of-Way', 'R5.N'): 'Foster Island Arboretum Deed',
    ('R - Right-of-Way', 'R5.O'): 'Arboretum Deed',
    ('R - Right-of-Way', 'R5.P'): 'Foster Island Easement',
    ('R - Right-of-Way', 'R6.A'): 'SR 5 Record of Survey',
    ('R - Right-of-Way', 'R6.B'): 'SR 520 Record of Survey',
    ('R - Right-of-Way', 'R6.C'): 'SR 513 Record of Survey',
    ('R - Right-of-Way', 'R6.D'): 'SR 520 SR 5 to 513 Record of Survey',
    ('R - Right-of-Way', 'R6.E'): 'Section 6F Record of Survey',
    ('R - Right-of-Way', 'R7.B'): 'TCE Leigh',
    ('R - Right-of-Way', 'R7.B.1'): 'TCE Construction Memo',
    ('R - Right-of-Way', 'R7.F'): 'RUP E Montlake Park',
    ('R - Right-of-Way', 'R7.G'): 'RUP Washington Park Arboretum',
    ('R - Right-of-Way', 'R7.H'): 'RUP Washington Park Arboretum WABN',
    ('R - Right-of-Way', 'R7.I'): 'RUP Lake Washington Blvd',
    ('R - Right-of-Way', 'R11'): 'Reports Survey Marks Primary Monumentation',
    ('R - Right-of-Way', 'R13'): 'Staging Areas Exhibit',
    ('R - Right-of-Way', 'R14'): 'State Sales Tax Rule 170 171 Map',

    # S - Structures (12 appendices from PDF)
    ('S - Structures', 'S1'): 'Design Criteria Essential Bridges',
    ('S - Structures', 'S2'): 'Seismic Design Criteria Lid Bridges',
    ('S - Structures', 'S3'): 'Light Rail Transit Loading',
    ('S - Structures', 'S4'): 'Sound Transit Design Criteria Manual',
    ('S - Structures', 'S5'): 'Seismic Isolation Design Criteria',
    ('S - Structures', 'S6'): 'Vessel Collision Data',
    ('S - Structures', 'S7'): 'Light Rail Ready White Paper',
    ('S - Structures', 'S8'): 'WABN Global Analysis Summary',
    ('S - Structures', 'S9'): 'Underwater Sound Levels Pile Driving',
    ('S - Structures', 'S10'): 'USCG Bridge Permit Application Guide',
    ('S - Structures', 'S11'): 'Structures Project Specifications',
    ('S - Structures', 'S12'): 'Existing Structural Elements Requirements',

    # T - Traffic (30 appendices from PDF)
    ('T - Traffic', 'T1'): 'Interchange Justification Report',
    ('T - Traffic', 'T2'): 'MicroSimulation Guidelines',
    ('T - Traffic', 'T4'): 'Approved Traffic Signal Permits',
    ('T - Traffic', 'T5'): 'Speed Limit Reductions Work Zones',
    ('T - Traffic', 'T6'): 'Work Zone Safety and Mobility',
    ('T - Traffic', 'T7'): 'WSP Traffic Control Assistance',
    ('T - Traffic', 'T8'): 'Signal Turn-On Checklist',
    ('T - Traffic', 'T9'): 'NCHRP Report 350',
    ('T - Traffic', 'T10'): 'FHWA TMP Work Zones',
    ('T - Traffic', 'T12'): 'NWR Sign Design Practices Manual',
    ('T - Traffic', 'T13'): 'NWR Traffic Operations Redbook',
    ('T - Traffic', 'T14'): 'NWR Signing Current Practices',
    ('T - Traffic', 'T15'): 'SIDRA Policy Settings',
    ('T - Traffic', 'T17'): 'SDOT VISSIM SCOOT Deployment Memo',
    ('T - Traffic', 'T18'): 'King County Metro ITS Requirements',
    ('T - Traffic', 'T19'): 'SDOT Pedestrian Mobility Work Zones',
    ('T - Traffic', 'T20'): 'SDOT Discretionary Guide Signs',
    ('T - Traffic', 'T22'): 'State Force Work Memo 1',
    ('T - Traffic', 'T23'): 'State Force Work Memo 2',
    ('T - Traffic', 'T24'): 'SDOT Sign Catalog',
    ('T - Traffic', 'T25'): 'Signing Inventory Form',
    ('T - Traffic', 'T26.A.1'): 'VISSIM Confidence Calibration AM',
    ('T - Traffic', 'T26.A.2'): 'VISSIM Confidence Calibration Mid',
    ('T - Traffic', 'T26.A.3'): 'VISSIM Confidence Calibration PM',
    ('T - Traffic', 'T26.B.1'): 'VISSIM Montlake Phase AM',
    ('T - Traffic', 'T26.B.2'): 'VISSIM Montlake Phase Mid',
    ('T - Traffic', 'T26.B.3'): 'VISSIM Montlake Phase PM',
    ('T - Traffic', 'T27'): 'Montlake Phase Traffic Operations Report',
    ('T - Traffic', 'T28'): 'Preferred Alternative Traffic Operations Report',
    ('T - Traffic', 'T29'): 'VISSIM Confidence Calibration Report',
    ('T - Traffic', 'T30'): 'WSDOT VISSIM Protocol',

    # TF - Transit Facilities (5 appendices from PDF)
    ('TF - Transit Facilities', 'TF2'): 'Metro Transportation Facility Design Guidelines',
    ('TF - Transit Facilities', 'TF3.A'): 'Metro Transit Passenger Facility Structural',
    ('TF - Transit Facilities', 'TF3.B'): 'Metro Transit Passenger Facility Details',
    ('TF - Transit Facilities', 'TF3.C'): 'Metro Transit Passenger Facility Structural',
    ('TF - Transit Facilities', 'TF4'): 'Metro Transit Trolley Overhead Standards',
    ('TF - Transit Facilities', 'TF5'): 'Metro Transit Signing Standards Manual',

    # U - Utilities (60+ appendices from PDF - massive category!)
    ('U - Utilities', 'U1.A'): 'CenturyLink Fiber Optic',
    ('U - Utilities', 'U1.B'): 'Comcast Cable Television',
    ('U - Utilities', 'U1.C.1'): 'R2016 GM381 Utility Agreement',
    ('U - Utilities', 'U1.C.2'): 'R2016 SAS 5573',
    ('U - Utilities', 'U1.C.3'): 'R2016 SAU 5571',
    ('U - Utilities', 'U1.C.4'): 'R2016 SAU 5572',
    ('U - Utilities', 'U1.C.5'): 'R2016 SAU 5574',
    ('U - Utilities', 'U1.C.6'): 'R2016 SAU 5595',
    ('U - Utilities', 'U1.C.7'): 'R2016 SAU 5596',
    ('U - Utilities', 'U1.C.8'): 'R2016 SUA 645-S2 647-S1',
    ('U - Utilities', 'U1.C.9'): 'R2016 SUA 657 Sup1',
    ('U - Utilities', 'U1.C.10'): 'R2016 SUA 658 5594',
    ('U - Utilities', 'U1.C.11'): 'R2016 SUA 658 Sup1',
    ('U - Utilities', 'U1.C.12'): 'R2016 SUA 658 Sup2',
    ('U - Utilities', 'U1.C.13'): 'R2016 UTB1141',
    ('U - Utilities', 'U1.C.14'): 'R2016 UTB1169',
    ('U - Utilities', 'U1.C.15'): 'R2016 UTB1170',
    ('U - Utilities', 'U1.C.16'): 'R2016 Westside SUA Locations',
    ('U - Utilities', 'U1.C.17'): 'SAU 5690 Utility Agreement',
    ('U - Utilities', 'U1.C.18'): 'SAU 5691 Utility Agreement',
    ('U - Utilities', 'U1.D'): 'King County Metro',
    ('U - Utilities', 'U1.E.1'): 'King County Sewer Siphon Photos',
    ('U - Utilities', 'U1.E.2'): 'King County Sewer Siphon As-Built',
    ('U - Utilities', 'U1.F'): 'Puget Sound Energy Gas',
    ('U - Utilities', 'U1.G'): 'Seattle City Light Electrical As-Built',
    ('U - Utilities', 'U1.H'): 'Seattle IT Fiber Optic As-Built',
    ('U - Utilities', 'U1.I'): 'SPU 12-inch Distribution Main',
    ('U - Utilities', 'U1.J'): 'SPU 54-inch Transmission Main',
    ('U - Utilities', 'U2.A.1'): '108 Inch CSS CCTV Inspection',
    ('U - Utilities', 'U2.A.2'): '108 Inch CSS CCTV Report',
    ('U - Utilities', 'U2.B.1'): '114 Inch CSS CCTV Inspection',
    ('U - Utilities', 'U2.B.2'): '114 Inch CSS CCTV Report',
    ('U - Utilities', 'U2.C.1'): '42 Inch CSS CCTV Inspection',
    ('U - Utilities', 'U2.C.2'): '42 Inch CSS CCTV Report',
    ('U - Utilities', 'U2.D.1'): 'CSS Water Line Potholing Results',
    ('U - Utilities', 'U2.D.2'): 'CSS Water Line Potholing Locations',
    ('U - Utilities', 'U3.A'): 'WSDOT Permit Franchise Database',
    ('U - Utilities', 'U3.B'): 'Utility Conflict Matrix',
    ('U - Utilities', 'U4'): 'Utility Contact List',
    ('U - Utilities', 'U5'): 'Utility Assignment of Rights',
    ('U - Utilities', 'U6'): 'KCWTD Feasibility Study',
    ('U - Utilities', 'U7'): 'SPU Feasibility Study',
    ('U - Utilities', 'U8.A'): 'KCWTD Design-Build Agreement',
    ('U - Utilities', 'U8.B'): 'SCL Design-Build Agreement',
    ('U - Utilities', 'U8.C'): 'Seattle IT Design-Build Agreement',
    ('U - Utilities', 'U8.D'): 'SPU Design-Build Agreement',
    ('U - Utilities', 'U8.E'): 'King County Metro Design-Build Agreement',
    ('U - Utilities', 'U9.A'): 'Comcast MOU',
    ('U - Utilities', 'U9.B'): 'PSE MOU',
    ('U - Utilities', 'U10.A'): 'CenturyLink Franchise Permits',
    ('U - Utilities', 'U10.B'): 'Comcast Franchise Permits',
    ('U - Utilities', 'U10.C'): 'FreshChoice Franchise',
    ('U - Utilities', 'U10.D'): 'Integra Telecom Franchise Permits',
    ('U - Utilities', 'U10.E'): 'King County Metro Franchise Permits',
    ('U - Utilities', 'U10.F'): 'LTS 360 Networks Franchise Permits',
    ('U - Utilities', 'U10.G'): 'PSE Franchise Permits',
    ('U - Utilities', 'U10.G.1'): 'PSE 24th Ave Franchise',
    ('U - Utilities', 'U10.H'): 'Seattle City Light Permits Franchises',
    ('U - Utilities', 'U10.I'): 'Seattle DOT Franchise Permits',
    ('U - Utilities', 'U10.J'): 'SPU Franchise Permits',
    ('U - Utilities', 'U10.K'): 'Sound Transit Franchise Permits',
    ('U - Utilities', 'U10.L'): 'Sprint Nextel Franchise Permits',
    ('U - Utilities', 'U10.M'): 'T-Mobile Permit UP17579',
    ('U - Utilities', 'U10.N'): 'Traylor Frontier Kemper Permit',
    ('U - Utilities', 'U10.O'): 'Verizon NW Franchise Permits',
    ('U - Utilities', 'U10.P'): 'XO Comm Franchise Permits',
    ('U - Utilities', 'U11'): 'SPU Special Provisions',
    ('U - Utilities', 'U12'): 'Sewer Line Min Cover Waterline Main',

    # V - Quality Assurance (2 appendices from PDF)
    ('V - Quality Assurance', 'V2'): 'QMP Outline',

    # X - Montlake Underlid Systems (7 appendices from PDF)
    ('X - Montlake Underlid Systems', 'X1.A'): 'Simplex Control System',
    ('X - Montlake Underlid Systems', 'X1.B'): 'Fire Alarm Response Flowchart',
    ('X - Montlake Underlid Systems', 'X2'): 'Conceptual Emergency Response',
    ('X - Montlake Underlid Systems', 'X3.A'): 'Seattle Fire Concurrence Letter 1',
    ('X - Montlake Underlid Systems', 'X4'): 'Montlake Underlid Concept of Operations',
    ('X - Montlake Underlid Systems', 'X5.A'): 'FLS Ventilation Corridor Study',
    ('X - Montlake Underlid Systems', 'X5.B'): 'Montlake Lid Egress Study',
    ('X - Montlake Underlid Systems', 'X5.C'): 'FLS Ventilation Corridor',
    ('X - Montlake Underlid Systems', 'X6'): 'Seattle NFPA 502 Amendments',
    ('X - Montlake Underlid Systems', 'X7'): 'WABN Emergency Response Plan',

    # Y - Montlake Phase Communications Plan (1 appendix from PDF)
    ('Y - Montlake Phase Communications Plan', 'Y1'): 'SR 520 Program No Surprises Approach',

    # Z - Community Workforce Agreement (1 appendix from PDF)
    ('Z - Community Workforce Agreement', 'Z1'): 'Community Workforce Agreement',
}

def find_pdf_in_nested_structure(category, appendix_id):
    """
    Find PDF file handling nested folder structures.

    Examples:
      D34.A -> D - Manuals / Appendix D34 / Appendix D34.A / *.pdf
      A-B2.A.1 -> A-B... / Appendix A-B2 / Appendix A-B2.A / Appendix A-B2.A.1 / *.pdf
      A4.1 -> A - Project Files / Appendix A4 / Appendix A4.1 / *.pdf
    """
    category_path = os.path.join(APPENDICES_DIR, category)

    if not os.path.exists(category_path):
        return None

    # First, try direct match (for simple appendices like D1, B14, etc.)
    simple_folder = os.path.join(category_path, f"Appendix {appendix_id}")
    if os.path.exists(simple_folder) and os.path.isdir(simple_folder):
        for item in os.listdir(simple_folder):
            if item.endswith('.pdf') and not item.startswith('.'):
                return os.path.join(simple_folder, item)

    # For nested appendices (contains dots), build path progressively
    if '.' in appendix_id:
        # Split by dots: D34.A -> ['D34', 'A'], A-B2.A.1 -> ['A-B2', 'A', '1']
        parts = appendix_id.split('.')

        # Start with base folder
        current_path = os.path.join(category_path, f"Appendix {parts[0]}")

        if not os.path.exists(current_path):
            return None

        # Navigate through nested folders
        for i in range(1, len(parts)):
            # Build cumulative appendix ID
            cumulative_id = '.'.join(parts[:i+1])

            # Try different naming patterns
            possible_names = [
                f"Appendix {cumulative_id}",
                cumulative_id,
            ]

            found_next = False
            for name in possible_names:
                next_path = os.path.join(current_path, name)
                if os.path.exists(next_path):
                    current_path = next_path
                    found_next = True
                    break

            if not found_next:
                # Couldn't find next level, stop here
                break

        # Search for PDF in the final folder
        if os.path.exists(current_path) and os.path.isdir(current_path):
            for item in os.listdir(current_path):
                if item.endswith('.pdf') and not item.startswith('.'):
                    return os.path.join(current_path, item)

    return None

def match_document_to_appendix(doc_name, full_name, category):
    """Match a document to its appendix."""
    # Normalize names for matching
    search_terms = []
    if full_name:
        search_terms.append(full_name.lower())
    if doc_name and doc_name != full_name:
        search_terms.append(doc_name.lower())

    best_match = None
    best_score = 0

    for (app_category, app_id), app_doc_name in APPENDIX_DATA.items():
        if app_category != category:
            continue

        app_doc_lower = app_doc_name.lower()

        for search_term in search_terms:
            # Check for substring matches
            if search_term in app_doc_lower or app_doc_lower in search_term:
                score = len(set(search_term.split()) & set(app_doc_lower.split()))
                if score > best_score:
                    best_score = score
                    best_match = app_id

    return best_match

def process_csv():
    """Process CSV and update with appendix file paths."""
    print("Loading CSV...")

    docs = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            docs.append(row)

    print(f"Loaded {len(docs)} documents")

    stats = {
        'total_processed': 0,
        'found': 0,
        'matched_but_no_file': 0,
        'not_matched': 0
    }

    report_lines = []

    for doc in docs:
        contract_section = doc.get('Contract_Section', '')
        rep_file = doc.get('Representative_File', '').strip()
        category = doc.get('Category', '').strip()
        doc_name = doc.get('Document_Name', '')
        full_name = doc.get('Full_Name', '').strip()
        doc_number = doc.get('Doc_Number', '')

        # Only process contract documents without files
        is_contract_doc = any(contract_section.startswith(f"{i}.") for i in range(1, 9))

        if not is_contract_doc or rep_file or not category:
            continue

        stats['total_processed'] += 1

        # Try to match to appendix
        appendix_id = match_document_to_appendix(doc_name, full_name, category)

        if appendix_id:
            # Try to find the file using FIXED nested search
            pdf_path = find_pdf_in_nested_structure(category, appendix_id)

            if pdf_path:
                filename = os.path.basename(pdf_path)
                doc['Representative_File'] = filename
                doc['File_Path'] = pdf_path
                doc['Files_Count'] = '1'

                stats['found'] += 1
                report_lines.append(f"✓ Doc #{doc_number}: {doc_name} -> Appendix {appendix_id} -> {filename}")
                print(f"✓ Found: Doc #{doc_number} -> {appendix_id}")
            else:
                stats['matched_but_no_file'] += 1
                report_lines.append(f"⚠ Doc #{doc_number}: {doc_name} -> Appendix {appendix_id} (file not found)")
                print(f"⚠ Matched but no file: Doc #{doc_number} -> {appendix_id}")
        else:
            stats['not_matched'] += 1
            report_lines.append(f"✗ Doc #{doc_number}: {doc_name} (no appendix match)")

    # Save updated CSV
    print(f"\nSaving updated CSV to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(docs)

    # Save report
    print(f"Saving report to {REPORT_TXT}...")
    with open(REPORT_TXT, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("COMPLETE APPENDIX MAPPING REPORT (WITH FIXED NESTED SEARCH)\n")
        f.write("=" * 100 + "\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 100 + "\n")
        f.write(f"Total documents processed:        {stats['total_processed']}\n")
        f.write(f"Successfully mapped:              {stats['found']}\n")
        f.write(f"Matched but file not found:       {stats['matched_but_no_file']}\n")
        f.write(f"Not matched to appendix:          {stats['not_matched']}\n\n")

        f.write("=" * 100 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 100 + "\n\n")

        for line in report_lines:
            f.write(line + "\n")

    print(f"\n{'=' * 80}")
    print("COMPLETE!")
    print(f"{'=' * 80}")
    print(f"Total documents processed:        {stats['total_processed']}")
    print(f"Successfully mapped:              {stats['found']}")
    print(f"Matched but file not found:       {stats['matched_but_no_file']}")
    print(f"Not matched to appendix:          {stats['not_matched']}")
    print(f"\nUpdated CSV: {OUTPUT_CSV}")
    print(f"Report: {REPORT_TXT}")

if __name__ == '__main__':
    process_csv()
