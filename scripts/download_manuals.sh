#!/bin/bash
# Download publicly available turbine manuals and documentation
# This script downloads all identified public PDFs for the Solaris Energy POC

set -e

MANUALS_DIR="../manuals"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="download_${TIMESTAMP}.log"

echo "Starting manual downloads at $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Function to download with retry
download_file() {
    local url=$1
    local output_path=$2
    local max_attempts=3
    local attempt=1
    
    echo "Downloading: $url" | tee -a "$LOG_FILE"
    echo "  -> $output_path" | tee -a "$LOG_FILE"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -L -o "$output_path" "$url" --connect-timeout 30 --max-time 300 2>&1 | tee -a "$LOG_FILE"; then
            if [ -f "$output_path" ] && [ -s "$output_path" ]; then
                echo "  ✓ Success (attempt $attempt)" | tee -a "$LOG_FILE"
                return 0
            fi
        fi
        echo "  ✗ Attempt $attempt failed, retrying..." | tee -a "$LOG_FILE"
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo "  ✗ Failed after $max_attempts attempts" | tee -a "$LOG_FILE"
    return 1
}

# Solaris Energy Infrastructure Company Materials
echo "" | tee -a "$LOG_FILE"
echo "=== Solaris Energy Infrastructure Materials ===" | tee -a "$LOG_FILE"

download_file \
    "https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris_5.7MW_Turbine_Power_-_Tech_Specs-243257d2.pdf" \
    "$MANUALS_DIR/SMT60-Taurus60/technical-specs/Solaris_SMT60_Technical_Specs.pdf"

download_file \
    "https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris_16.5MW_Turbine_Power_-_Tech_Specs.pdf" \
    "$MANUALS_DIR/SMT130-Titan130/technical-specs/Solaris_SMT130_Technical_Specs.pdf"

download_file \
    "https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris_35MW_Turbine_Power_-_Tech_Specs-83f9c921.pdf" \
    "$MANUALS_DIR/TM2500-LM2500/technical-specs/Solaris_TM2500_Technical_Specs.pdf"

download_file \
    "https://ir.solaris-energy.com/~/media/Files/S/Solaris-IR/reports-and-presentations/sei-investor-presentation-august-2025.pdf" \
    "$MANUALS_DIR/general/reference/SEI_Investor_Presentation_Aug2025.pdf"

download_file \
    "https://ir.solaris-energy.com/~/media/Files/S/Solaris-IR/reports-and-presentations/sei-investor-presentation-may-2025.pdf" \
    "$MANUALS_DIR/general/reference/SEI_Investor_Presentation_May2025.pdf"

# Solar Turbines Materials (Taurus 60 & Titan 130)
echo "" | tee -a "$LOG_FILE"
echo "=== Solar Turbines Materials ===" | tee -a "$LOG_FILE"

download_file \
    "https://www.aaronequipment.com/equipmentattachments/11729003_solar_taurus_60_gas_turbine_generator.pdf" \
    "$MANUALS_DIR/SMT60-Taurus60/reference/Solar_Taurus60_Spec_Sheet.pdf"

download_file \
    "https://mcatradeandlearn.com/wp-content/uploads/2020/11/Solar-Turbine-Produt-Handbook-for-Power-Generation.pdf" \
    "$MANUALS_DIR/general/reference/Solar_Turbines_Product_Handbook.pdf"

# GE LM2500+G4 Materials
echo "" | tee -a "$LOG_FILE"
echo "=== GE LM2500+G4 Materials ===" | tee -a "$LOG_FILE"

download_file \
    "https://mscn7training.com/wp-content/uploads/2021/01/MSC01A_1211_B5_LM2500-Gas-Turbine_-r5b_rg.pdf" \
    "$MANUALS_DIR/TM2500-LM2500/operational/LM2500_Training_Manual.pdf"

download_file \
    "https://www.gevernova.com/content/dam/gepower-new/global/en_US/downloads/gas-new-site/resources/reference/ger-4250-ge-lm2500-g4-aero-gas-turbine-marine-industrial-applications.pdf" \
    "$MANUALS_DIR/TM2500-LM2500/reference/GER-4250_LM2500G4_Technical_Reference.pdf"

download_file \
    "https://www.geaerospace.com/sites/default/files/datasheet-lm2500plusg4.pdf" \
    "$MANUALS_DIR/TM2500-LM2500/technical-specs/LM2500G4_Datasheet.pdf"

download_file \
    "https://vbr-turbinepartners.com/wp-content/uploads/2023/03/Training-course-LM2500-Elst-42608777-April-2023.pdf" \
    "$MANUALS_DIR/TM2500-LM2500/reference/LM2500_Training_Course_Info.pdf"

download_file \
    "https://gasturbinesystems.files.wordpress.com/2018/06/lm2500-pocketguide.pdf" \
    "$MANUALS_DIR/TM2500-LM2500/reference/LM2500_Pocket_Guide.pdf"

# Battery Energy Storage System (BESS) Safety Materials
echo "" | tee -a "$LOG_FILE"
echo "=== BESS Safety Materials ===" | tee -a "$LOG_FILE"

download_file \
    "https://www.bakerrisk.com/wp-content/uploads/2024/03/BESS-White-Papers-1-7-Combined.pdf" \
    "$MANUALS_DIR/BESS/safety/BESS_Incidents_Risk_Management_BakerRisk.pdf"

download_file \
    "https://assets.thehartford.com/image/upload/fire_hazards_of_battery_energy_storage_systems.pdf" \
    "$MANUALS_DIR/BESS/safety/Fire_Hazards_BESS_Hartford.pdf"

# Summary
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Download process completed at $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Count successful downloads
SUCCESS_COUNT=$(find "$MANUALS_DIR" -type f -name "*.pdf" | wc -l | tr -d ' ')
echo "Successfully downloaded: $SUCCESS_COUNT PDFs" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Display directory structure
echo "Directory structure:" | tee -a "$LOG_FILE"
tree -L 3 "$MANUALS_DIR" 2>/dev/null || find "$MANUALS_DIR" -type f -name "*.pdf" | sort | tee -a "$LOG_FILE"

