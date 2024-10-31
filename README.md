# STP Registration Pipeline Documentation
Version 1.0

## Table of Contents
- [Introduction](#introduction)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Pipeline Overview](#pipeline-overview)
- [Directory Structure](#directory-structure)
- [Detailed Pipeline Stages](#detailed-pipeline-stages)
  - [1. Preprocessing](#1-preprocessing-stage)
  - [2. Registration](#2-registration-stage)
  - [3. Atlas Transfer](#3-atlas-transfer-stage)
  - [4. Video Generation](#4-video-generation-stage)
  - [5. Target Transfer](#5-target-transfer-stage)
  - [6. JSON Generation](#6-json-generation-stage)
  - [7. Injection Detection](#7-injection-detection-stage)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [FAQ](#faq)

## Introduction

The Serial Two-Photon (STP) Registration Pipeline is a comprehensive suite of tools designed for processing and analyzing brain imaging data. This pipeline handles everything from initial image preprocessing to final visualization preparation, with a focus on accurate registration and atlas mapping.

### Key Features
- Automated preprocessing of STP imaging data
- LDDMM-based registration
- Atlas region mapping
- Injection site detection
- Web portal data preparation
- Batch processing capabilities
- Cluster computing integration

## System Requirements

### Hardware Requirements
- Minimum 16GB RAM (32GB recommended)
- Multi-core processor
- Sufficient storage space (500GB+ recommended)

### Software Requirements
- Unix/Linux operating system
- Python 3.7+
  - NumPy
  - SciPy
  - Other dependencies (requirements.txt provided)
- ImageMagick
- Kakadu tools for JP2 compression
- Grid Engine (SGE/UGE) for cluster computing

## Installation

### 1. System Packages
```bash
# Update system
sudo apt-get update

# Install required packages
sudo apt-get install imagemagick python3-pip
```

### 2. Python Dependencies
```bash
# Install Python requirements
pip3 install -r requirements.txt
```

### 3. Environment Setup
```bash
# Set up environment variables
export PIPELINE_DIR=/path/to/STP_RegistrationData
export PATH=$PIPELINE_DIR/bins:$PATH
```
## Pipeline Overview

The pipeline consists of seven main stages:

1. **Preprocessing** - Image preparation and standardization
2. **Registration** - LDDMM-based alignment
3. **Atlas Transfer** - Mapping of atlas regions
4. **Video Generation** - Visualization creation
5. **Target Transfer** - Portal data preparation
6. **JSON Generation** - Metadata creation
7. **Injection Detection** - Analysis of injection sites

## Directory Structure
```
STP_RegistrationData/
├── bins/                    # Binary and script files
│   ├── 1.Preprocessing/     # Preprocessing scripts
│   ├── 2.LddmmRegistration/ # Registration algorithms
│   ├── 3.Transformation/    # Transform tools
│   └── 5.MakeJson/         # JSON generation scripts
├── data/                    # Data directory
│   ├── preprocessing/       # Preprocessed images
│   ├── transfer_para/       # Transfer parameters
│   ├── toPortal/           # Portal-ready data
│   ├── bnb_outputs/        # Processing outputs
│   └── bnb_errors/         # Error logs
└── Lists/                   # Batch processing lists
```

## Detailed Pipeline Stages

### 1. Preprocessing Stage
**Script**: `pipeline1_preprocessing.sh`

#### Purpose
Prepares raw brain imaging data for registration by standardizing format and resolution.

#### Usage
```bash
./pipeline1_preprocessing.sh <mode> <brain_id>

# Single brain processing
./pipeline1_preprocessing.sh -single BRAIN123

# Batch processing
./pipeline1_preprocessing.sh -list brain_list.txt
```

#### Parameters
- `mode`: Processing mode (`-single` or `-list`)
- `brain_id`: Individual brain ID or path to list file

#### Output
- Standardized images in `/data/preprocessing/`
- Processing logs
- Quality check reports

### 2. Registration Stage
**Script**: `pipeline2_registration.sh`

#### Purpose
Performs LDDMM registration to align brain images with standard space.

#### Usage
```bash
./pipeline2_registration.sh <mode> <brain_id>
```

#### Technical Details
- Uses multi-threaded LDDMM implementation
- Memory usage: ~2GB per thread
- Typical runtime: 2-4 hours per brain
- Output stored in `data/transfer_para/`
### 3. Atlas Transfer Stage
**Script**: `pipeline3_TransferAtlas.sh`

#### Purpose
Maps atlas annotations onto registered brain images.

#### Usage
```bash
./pipeline3_TransferAtlas.sh <mode> <brain_id>
```

#### Process Flow
1. Load registration parameters
2. Transform atlas coordinates
3. Generate overlay maps
4. Verify mapping accuracy

### 4. Video Generation Stage
**Script**: `pipeline3.5_Video.sh`

#### Purpose
Creates visualization sequences of registration results.

#### Usage
```bash
./pipeline3.5_Video.sh <brain_id>
```

#### Output
- MP4 visualization sequences
- Frame-by-frame images
- Quality control metrics

### 5. Target Transfer Stage
**Script**: `pipeline4_TransferTarget.sh`

#### Purpose
Prepares data for web portal visualization.

#### Usage
```bash
./pipeline4_TransferTarget.sh <mode> <brain_id>
```

#### Features
- Image format conversion
- JP2 compression
- Thumbnail generation
- Directory structure creation

#### Technical Commands
```bash
# Image rotation and compression
convert input.tif -rotate 90 -compress None output.tif

# JP2 compression
kdu_compress -i input.tif -o output.jp2 -num_threads 16 -rate 1.0 \
    Creversible=yes Sprecision=16 Ssigned=no -full -precise \
    Clevels=7 Clayers=8 Qstep=0.00001
```

### 6. JSON Generation Stage
**Script**: `pipeline5_ProduceJson.sh`

#### Purpose
Creates metadata files for web interface integration.

#### Usage
```bash
./pipeline5_ProduceJson.sh <mode> <brain_id>
```

#### JSON Structure Example
```json
TODO
```
### 7. Injection Detection Stage
**Script**: `pipeline6_InjectionDetection.sh`

#### Purpose
Analyzes and documents injection sites.

#### Usage
```bash
./pipeline6_InjectionDetection.sh <brain_id>
```

## Usage Guide

### Basic Workflow
```bash
# 1. Single brain processing
./pipeline1_preprocessing.sh -single BRAIN123
./pipeline2_registration.sh -single BRAIN123
./pipeline3_TransferAtlas.sh -single BRAIN123
./pipeline4_TransferTarget.sh -single BRAIN123
./pipeline5_ProduceJson.sh -single BRAIN123

# 2. Batch processing
./pipeline1_preprocessing.sh -list brain_list.txt
./pipeline2_registration.sh -list brain_list.txt
./pipeline3_TransferAtlas.sh -list brain_list.txt
./pipeline4_TransferTarget.sh -list brain_list.txt
./pipeline5_ProduceJson.sh -list brain_list.txt

# 3. Automated processing using PipelineX
./pipelineX.sh BRAIN123
```

### Data Requirements
- Input images must be in TIFF format
- Resolution: 0.46µm x 0.46µm x (z spacing)µm
- 16-bit depth recommended
- Proper naming convention: `BRAIN123_section_*.tif`

## Troubleshooting

### Common Issues and Solutions

1. **Memory Errors**
```bash
# Symptom: Process killed during registration
# Solution: Adjust memory allocation
-l m_mem_free=4G  # Increase as needed
```

2. **Missing Files**
   - Check input data paths
   - Verify directory permissions
   - Ensure all dependencies are installed

3. **Cluster Issues**
   - Monitor queue status: `qstat`
   - Check error logs: `data/bnb_errors/`
   - Verify resource availability

## Advanced Configuration

### Environment Variables
```bash
# Base configuration
export PIPELINE_DIR=/path/to/STP_RegistrationData
export BASELOC=$PIPELINE_DIR/bins
export OUTPUT_DIR=$PIPELINE_DIR/data

# Performance tuning
export NUM_THREADS=16
export MEM_PER_THREAD=2G
```

### Performance Optimization
- Adjust thread count based on available cores
- Balance memory allocation
- Monitor I/O performance
- Use local scratch space for temporary files

## FAQ



For technical support or questions:
1. Check error logs in `data/bnb_errors/`
2. Review pipeline documentation

---

*Last updated: [Current Date]*