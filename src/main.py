"""
ETL Pipeline Main Orchestrator
Coordinates the Extract, Transform, Load operations
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from utils.logger import get_logger
from etl.extract import DataExtractor
from etl.transform import DataTransformer
from etl.load import DataLoader
from database.connection import DatabaseManager

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class ETLPipeline:
    """Main ETL Pipeline orchestrator"""
    
    def __init__(self):
        """Initialize ETL Pipeline components"""
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.db_manager = DatabaseManager()
        
    def run_full_pipeline(self):
        """Execute the complete ETL pipeline"""
        try:
            logger.info("Starting ETL Pipeline execution")
            
            # Step 1: Extract
            logger.info("Step 1: Data Extraction")
            raw_data = self.extractor.extract_data()
            
            if raw_data is None:
                raise Exception("Data extraction failed")
            
            logger.info(f"Successfully extracted {len(raw_data)} records")
            
            # Step 2: Transform
            logger.info("Step 2: Data Transformation")
            transformed_data = self.transformer.transform_data(raw_data)
            
            if transformed_data is None:
                raise Exception("Data transformation failed")
            
            logger.info(f"Successfully transformed {len(transformed_data)} records")
            
            # Step 3: Load
            logger.info("Step 3: Data Loading")
            success = self.loader.load_data(transformed_data)
            
            if not success:
                raise Exception("Data loading failed")
            
            logger.info("ETL Pipeline completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {str(e)}")
            return False
    
    def run_sql_analysis(self):
        """Execute SQL analysis queries"""
        try:
            logger.info("Starting SQL Analysis")
            
            # Connect to database
            with self.db_manager.get_connection() as conn:
                # Run analysis queries
                # This will be populated with specific queries based on dataset
                logger.info("SQL Analysis completed successfully")
                
        except Exception as e:
            logger.error(f"SQL Analysis failed: {str(e)}")


def main():
    """Main execution function"""
    pipeline = ETLPipeline()
    
    # Run ETL Pipeline
    success = pipeline.run_full_pipeline()
    
    if success:
        # Run SQL Analysis
        pipeline.run_sql_analysis()
    else:
        logger.error("ETL Pipeline failed, skipping SQL analysis")
        sys.exit(1)


if __name__ == "__main__":
    main()