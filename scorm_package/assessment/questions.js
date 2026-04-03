/*
 * Quiz Question Bank
 * Cloud Computing: Multi-Cloud Migration Strategy — GCP to AWS
 * 15 multiple-choice questions (5 per module)
 */

var defined_questions = [

    // =========================================
    // Module 1: Strategic Assessment and Service Mapping (Q1-Q5)
    // =========================================
    {
        id: "m1_q1",
        module: 1,
        text: "According to Flexera's 2023 State of the Cloud Report, what percentage of enterprises operate multi-cloud environments?",
        answers: ["62%", "75%", "87%", "94%"],
        correct: 2
    },
    {
        id: "m1_q2",
        module: 1,
        text: "When mapping GCP services to AWS, which GCP service maps to Amazon Redshift?",
        answers: ["Cloud Spanner", "Cloud SQL", "BigQuery", "Firestore"],
        correct: 2
    },
    {
        id: "m1_q3",
        module: 1,
        text: "In the 6R migration strategy, which approach involves moving an application to a SaaS offering?",
        answers: ["Rehost", "Replatform", "Refactor", "Repurchase"],
        correct: 3
    },
    {
        id: "m1_q4",
        module: 1,
        text: "What is the primary architectural difference between GCP VPC and AWS VPC?",
        answers: [
            "GCP VPC is regional while AWS VPC is global",
            "GCP VPC is global while AWS VPC is regional",
            "Both are global in scope",
            "Both are regional in scope"
        ],
        correct: 1
    },
    {
        id: "m1_q5",
        module: 1,
        text: "What is the recommended first phase of a wave planning methodology?",
        answers: [
            "Foundation Wave — set up core infrastructure",
            "Production Wave — migrate critical applications",
            "Pilot Wave — 1-3 low-risk applications",
            "Optimization Phase — right-size resources"
        ],
        correct: 2
    },

    // =========================================
    // Module 2: Technical Migration Execution (Q6-Q10)
    // =========================================
    {
        id: "m2_q1",
        module: 2,
        text: "When converting Terraform configurations from GCP to AWS, what primary change is required?",
        answers: [
            "Switching from HCL to YAML syntax",
            "Changing the provider block from 'google' to 'aws'",
            "Rewriting all modules in CloudFormation",
            "Converting to Pulumi for cross-cloud support"
        ],
        correct: 1
    },
    {
        id: "m2_q2",
        module: 2,
        text: "Which AWS service achieves transfer speeds up to 10x faster than open-source tools for object storage migration?",
        answers: ["AWS Transfer Family", "AWS DataSync", "AWS Snowball", "S3 Transfer Acceleration"],
        correct: 1
    },
    {
        id: "m2_q3",
        module: 2,
        text: "What is the recommended target replication lag for AWS DMS before a production database cutover?",
        answers: ["Under 60 seconds", "Under 30 seconds", "Under 5 seconds", "Under 1 second"],
        correct: 2
    },
    {
        id: "m2_q4",
        module: 2,
        text: "During DNS-based traffic shifting with Route 53, what is the recommended initial traffic percentage to route to AWS?",
        answers: ["5%", "10%", "25%", "50%"],
        correct: 1
    },
    {
        id: "m2_q5",
        module: 2,
        text: "What loading format provides approximately 4x faster Redshift ingestion compared to CSV?",
        answers: ["JSON", "Avro", "Parquet", "ORC"],
        correct: 2
    },

    // =========================================
    // Module 3: Optimization and Operational Excellence (Q11-Q15)
    // =========================================
    {
        id: "m3_q1",
        module: 3,
        text: "What percentage of cloud spend is typically attributed to compute resources?",
        answers: ["30-40%", "40-50%", "50-60%", "60-70%"],
        correct: 3
    },
    {
        id: "m3_q2",
        module: 3,
        text: "AWS Savings Plans offer discounts of up to what percentage compared to On-Demand pricing?",
        answers: ["50%", "60%", "72%", "85%"],
        correct: 2
    },
    {
        id: "m3_q3",
        module: 3,
        text: "What is the recommended coverage ratio for baseline compute through Savings Plans vs On-Demand/Spot?",
        answers: [
            "50-60% Savings Plans, 40-50% On-Demand/Spot",
            "60-70% Savings Plans, 30-40% On-Demand/Spot",
            "70-80% Savings Plans, 20-30% On-Demand/Spot",
            "90-100% Savings Plans, 0-10% On-Demand/Spot"
        ],
        correct: 2
    },
    {
        id: "m3_q4",
        module: 3,
        text: "Amazon Aurora PostgreSQL achieves approximately how many times the throughput of standard PostgreSQL?",
        answers: ["1.5x", "2x", "3x", "5x"],
        correct: 2
    },
    {
        id: "m3_q5",
        module: 3,
        text: "By how much can Amazon ElastiCache reduce database queries for read-heavy applications?",
        answers: ["30-50%", "50-70%", "70-90%", "90-99%"],
        correct: 2
    }
];
