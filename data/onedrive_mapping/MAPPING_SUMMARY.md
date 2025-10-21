# OneDrive to CSV Mapping Summary

## Current Status

**Found from initial mapping:**
- Contract documents with files already mapped: **223**
- Contract documents missing files: **561**

**Files successfully mapped in this session:**
- Only **2-3** additional matches found using automated name matching

## Why Automated Matching Failed

The OneDrive structure uses **numbered appendices**, while the CSV uses **descriptive document names**:

### OneDrive Structure
```
Appendices/
  ├── A - Project Files/
  │   ├── Appendix A1/
  │   ├── Appendix A2/
  │   └── Appendix A3/
  ├── D - Manuals/
  │   ├── Appendix D1/
  │   │   └── Appendix D1.pdf
  │   ├── Appendix D2/
  │   │   └── Appendix D2.pdf
  │   └── ... (49 total appendices)
  └── [Other categories...]
```

### CSV Structure
```
Doc #137: Bridge Deck Protection System (Category: D - Manuals)
Doc #138: Bridge Design Manual (Category: D - Manuals)
Doc #139: Bridge Design Minimum Requirements (Category: D - Manuals)
...
```

**The mapping we need:** Which appendix number corresponds to which document name?
- Is "Bridge Deck Protection System" = Appendix D1? Or D2? Or D10?
- Is "Bridge Design Manual" = Appendix D1? Or D2?

## The Solution: Appendices List.pdf

There is an "Appendices List.pdf" file that contains the master mapping:

**Location:**
```
/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Contract Documents/Appendices/Appendices List.pdf
```

This PDF file should contain a table that maps:
- Appendix Number (e.g., "D1", "D2", "E1", etc.)
- To Document Name (e.g., "Bridge Deck Protection System")

## OneDrive Appendices Inventory

| Category | # of Appendices | Example Appendices |
|----------|----------------|-------------------|
| A - Project Files | 4 | A1, A2, A3, A4 |
| A-B - As-Built Plans and Construction | 11 | A-B1, A-B2, ... A-B11 |
| B - Specifications | 16 | B1, B2, ... B16 |
| C - Commitments List | 1 | C1 |
| **D - Manuals** | **49** | D1, D2, ... D44 |
| **E - Environmental** | **38** | E1, E2, ... E38 |
| F - Forms | 8 | F1, F2, ... F8 |
| G - Geotechnical | 25 | G1, G2, ... G25 |
| H - Hydraulics | 16 | H1, H2, ... H16 |
| I - Illumination, Electrical & ITS | 23 | I1, I2, ... I23 |
| J - Pavement | 4 | J1, J2, J3, J4 |
| K - Prevailing Wages | 2 | K1, K2 |
| L - Landscape and Urban Design | 14 | L1, L2, ... L14 |
| M - Conceptual Plans | 22 | M1, M2, ... M22 |
| N - Local Agency Agreements | 4 | N1, N2, N3, N4 |
| O - Design Documentation | 15 | O1, O2, ... O15 |
| P - Permits and Approvals | 7 | P1, P2, ... P7 |
| R - Right-of-Way | 15 | R1, R2, ... R15 |
| S - Structures | 12 | S1, S2, ... S12 |
| T - Traffic | 30 | T1, T2, ... T30 |
| TF - Transit Facilities | 5 | TF1, ... TF5 |
| U - Utilities | 12 | U1, U2, ... U12 |
| V - Quality Assurance | 2 | V1, V2 |
| X - Montlake Underlid Systems | 7 | X1, X2, ... X7 |
| Y - Montlake Phase Communications Plan | 1 | Y1 |
| Z - Community Workforce Agreement | 1 | Z1 |

**Total Appendices Found:** ~350+

## Next Steps

### Option 1: Extract Mapping from Appendices List.pdf
1. Open the Appendices List.pdf
2. Extract the table that maps appendix numbers to document names
3. Create a lookup file (CSV or JSON)
4. Run an updated mapping script using this lookup

### Option 2: Manual Mapping (Small Sample)
If you only need to verify a few critical documents, you can:
1. Open the relevant appendix PDF
2. Verify it matches the expected document
3. Manually update the CSV

### Option 3: OCR/Parse the PDF
Use a PDF parsing tool to automatically extract the appendix number → document name mapping from the Appendices List.pdf

## Files Created

- `contract_docs_mapping.csv` - Spreadsheet of current mappings
- `contract_docs_mapping.json` - JSON of current mappings
- `contract_docs_mapping.txt` - Human-readable report
- `onedrive_structure.json` - Complete OneDrive folder/file inventory
- `requirements_tracker_updated.csv` - Updated CSV (with minimal changes)
- `mapping_report.txt` - Detailed mapping attempt report

## Summary

The CSV was originally created by mapping OneDrive to document names, and that original mapping used the **Appendices List.pdf** as the source of truth. To complete the mapping for the 561 missing documents, we need to:

1. **Extract the data from Appendices List.pdf** (the master mapping)
2. Use that mapping to match appendix numbers to CSV document names
3. Update the CSV with the correct file paths

The infrastructure is in place - we just need the appendix number → document name lookup table!
