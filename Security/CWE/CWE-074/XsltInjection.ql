/**
 * @name XSLT transformation with user-controlled stylesheet
 * @description Performing an XSLT transformation with user-controlled stylesheets can lead to
 *              information disclosure or execution of arbitrary code.
 * @kind path-problem
 * @problem.severity error
 * @precision high
 * @id java/xslt-injection
 * @tags security
 *       external/cwe/cwe-074
 */

import java
import semmle.code.java.security.XsltInjectionQuery
import DataFlow::PathGraph

from DataFlow::PathNode source, DataFlow::PathNode sink, XsltInjectionFlowConfig conf
where conf.hasFlowPath(source, sink)
select sink.getNode().getLocation().toString()
