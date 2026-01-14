"""
Test Suite for Multi-Agent Legal Reasoning System

Run with: python test_system.py
"""

import sys
import time
from datetime import datetime
from typing import Dict, Any

from schemas.messages import UserQuery
from chains import invoke_chain
from logging.audit import get_audit_logger


class SystemTester:
    """Test harness for the multi-agent system."""
    
    def __init__(self):
        self.test_results = []
        self.audit_logger = get_audit_logger()
    
    def run_test(self, test_name: str, query: UserQuery) -> Dict[str, Any]:
        """Run a single test case."""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        print(f"Question: {query.question}")
        if query.case_context:
            print(f"Context: {query.case_context}")
        print()
        
        try:
            start_time = time.time()
            result = invoke_chain(query)
            execution_time = time.time() - start_time
            
            # Determine test outcome
            result_type = type(result).__name__
            
            print(f"Result Type: {result_type}")
            print(f"Execution Time: {execution_time:.2f}s")
            
            if hasattr(result, 'status'):
                print(f"Status: {result.status}")
            
            if hasattr(result, 'confidence'):
                print(f"Confidence: {result.confidence}")
            
            # Store result
            test_result = {
                "test_name": test_name,
                "success": True,
                "result_type": result_type,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.test_results.append(test_result)
            
            print(f"\n✅ Test PASSED")
            return test_result
            
        except Exception as e:
            print(f"\n❌ Test FAILED: {str(e)}")
            test_result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.test_results.append(test_result)
            return test_result
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        
        if failed > 0:
            print(f"\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result.get('error', 'Unknown error')}")
        
        print(f"\n{'='*60}\n")


def main():
    """Run all tests."""
    tester = SystemTester()
    
    # Test 1: Basic legal query
    tester.run_test(
        "Basic Legal Definition",
        UserQuery(
            question="What is the definition of culpable homicide under Sri Lankan law?",
            case_context=None
        )
    )
    
    # Test 2: Query with context
    tester.run_test(
        "Query with Case Context",
        UserQuery(
            question="What are the penalties for this offense?",
            case_context="A person caused death with intention but without premeditation."
        )
    )
    
    # Test 3: Specific section query
    tester.run_test(
        "Specific Section Query",
        UserQuery(
            question="What does Section 299 of the Penal Code say?",
            case_context=None
        )
    )
    
    # Test 4: Complex legal question
    tester.run_test(
        "Complex Legal Question",
        UserQuery(
            question="What is the difference between culpable homicide and murder under Sri Lankan law?",
            case_context=None
        )
    )
    
    # Test 5: Likely to cause refusal (insufficient sources)
    tester.run_test(
        "Obscure Legal Topic",
        UserQuery(
            question="What are the legal implications of quantum computing on intellectual property law in Sri Lanka?",
            case_context=None
        )
    )
    
    # Print summary
    tester.print_summary()
    
    # Export audit logs
    print("Exporting audit logs...")
    json_file = tester.audit_logger.export_session_logs()
    md_file = tester.audit_logger.generate_audit_report()
    
    print(f"✅ JSON logs: {json_file}")
    print(f"✅ Markdown report: {md_file}")
    print()


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║   SentiLex AI Advocate - System Test Suite               ║
║   Multi-Agent Legal Reasoning System                      ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        sys.exit(1)
