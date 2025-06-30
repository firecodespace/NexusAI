import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  VStack,
  HStack,
  Icon,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Badge,
  Progress,
  Tooltip,
  Flex,
  Divider,
} from '@chakra-ui/react';
import { FiUpload, FiFileText, FiRefreshCw, FiTrendingUp, FiDollarSign, FiCalendar, FiCheckCircle, FiAlertCircle, FiClock } from 'react-icons/fi';
import { Link as RouterLink } from 'react-router-dom';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalInvoices: 0,
    processedInvoices: 0,
    totalAmount: 0,
    pendingValidation: 0,
  });
  const [recentInvoices, setRecentInvoices] = useState([]);
  const [cashFlowAnalysis, setCashFlowAnalysis] = useState(null);
  const [gstComplianceAnalysis, setGstComplianceAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.600');

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching dashboard data...');
      
      const response = await fetch('http://localhost:8000/api/v1/invoices/dashboard');
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Received data:', data);
      
      if (!data || !data.stats) {
        console.error('Invalid data format:', data);
        throw new Error('Invalid data format received from server');
      }

      setStats(data.stats || {
        totalInvoices: 0,
        processedInvoices: 0,
        totalAmount: 0,
        pendingValidation: 0,
      });
      setRecentInvoices(data.recentInvoices || []);
      setCashFlowAnalysis(data.cashFlowAnalysis || null);
      setGstComplianceAnalysis(data.gstComplianceAnalysis || null);
      
      toast({
        title: 'Dashboard updated',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError(error.message);
      toast({
        title: 'Error loading dashboard',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'processed':
        return 'green';
      case 'pending':
        return 'yellow';
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" mb={4} borderRadius="md">
        <AlertIcon />
        <Box flex="1">
          <AlertTitle>Error loading dashboard</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Box>
        <Button
          leftIcon={<Icon as={FiRefreshCw} />}
          onClick={fetchDashboardData}
          colorScheme="red"
          variant="outline"
          size="sm"
        >
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box p={4}>
      <HStack justify="space-between" mb={6}>
        <Heading size="lg">Dashboard</Heading>
        <Button
          leftIcon={<Icon as={FiRefreshCw} />}
          onClick={fetchDashboardData}
          size="sm"
          isLoading={loading}
        >
          Refresh
        </Button>
      </HStack>
      
      {/* Quick Actions */}
      <HStack spacing={4} mb={8}>
        <Button
          as={RouterLink}
          to="/upload"
          leftIcon={<Icon as={FiUpload} />}
          colorScheme="blue"
          size="lg"
        >
          Upload Invoice
        </Button>
        <Button
          as={RouterLink}
          to="/invoices"
          leftIcon={<Icon as={FiFileText} />}
          variant="outline"
          size="lg"
        >
          View All Invoices
        </Button>
      </HStack>

      {/* Statistics */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }} transition="all 0.2s">
          <CardBody>
            <Stat>
              <StatLabel color="gray.500">Total Invoices</StatLabel>
              <StatNumber fontSize="3xl">{stats.totalInvoices}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                23.36%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }} transition="all 0.2s">
          <CardBody>
            <Stat>
              <StatLabel color="gray.500">Processed</StatLabel>
              <StatNumber fontSize="3xl">{stats.processedInvoices}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                15.2%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }} transition="all 0.2s">
          <CardBody>
            <Stat>
              <StatLabel color="gray.500">Total Amount</StatLabel>
              <StatNumber fontSize="3xl">{formatCurrency(stats.totalAmount)}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                12.5%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }} transition="all 0.2s">
          <CardBody>
            <Stat>
              <StatLabel color="gray.500">Pending Validation</StatLabel>
              <StatNumber fontSize="3xl">{stats.pendingValidation}</StatNumber>
              <StatHelpText>
                <StatArrow type="decrease" />
                8.1%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Charts and Analytics */}
      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6} mb={8}>
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
          <CardHeader>
            <Heading size="md">Invoice Volume Trend</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats.monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" name="Invoices" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>

        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
          <CardHeader>
            <Heading size="md">Amount Distribution</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.amountDistribution}
                    dataKey="count"
                    nameKey="range"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {stats.amountDistribution?.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </Grid>

      {/* Cash Flow Analysis */}
      {cashFlowAnalysis && (
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={8}>
          <CardHeader>
            <Heading size="md">Cash Flow Analysis</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={6} align="stretch">
              {/* Cash Flow Overview */}
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
                <Stat>
                  <StatLabel>Total Inflow</StatLabel>
                  <StatNumber color="green.600">{formatCurrency(cashFlowAnalysis.totalInflow)}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Total Outflow</StatLabel>
                  <StatNumber color="red.600">{formatCurrency(cashFlowAnalysis.totalOutflow)}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Net Cash Flow</StatLabel>
                  <StatNumber color={cashFlowAnalysis.netCashFlow >= 0 ? "green.600" : "red.600"}>
                    {formatCurrency(cashFlowAnalysis.netCashFlow)}
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Daily Average</StatLabel>
                  <StatNumber>{formatCurrency(cashFlowAnalysis.averageDailyFlow)}</StatNumber>
                </Stat>
              </SimpleGrid>

              {/* Cash Flow Trend */}
              <Box>
                <HStack justify="space-between" mb={4}>
                  <Text fontWeight="bold">Cash Flow Trend</Text>
                  <Badge 
                    colorScheme={
                      cashFlowAnalysis.cashFlowTrend === "increasing" ? "green" :
                      cashFlowAnalysis.cashFlowTrend === "decreasing" ? "red" : "yellow"
                    }
                  >
                    {cashFlowAnalysis.cashFlowTrend.toUpperCase()}
                  </Badge>
                </HStack>
              </Box>

              {/* Monthly Breakdown Chart */}
              {cashFlowAnalysis.monthlyBreakdown && cashFlowAnalysis.monthlyBreakdown.length > 0 && (
                <Box>
                  <Text fontWeight="bold" mb={4}>Monthly Cash Flow</Text>
                  <Box h="300px">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={cashFlowAnalysis.monthlyBreakdown}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <RechartsTooltip formatter={(value) => formatCurrency(value)} />
                        <Legend />
                        <Bar dataKey="total_amount" fill="#8884d8" name="Total Amount" />
                        <Bar dataKey="gst_collected" fill="#82ca9d" name="GST Collected" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </Box>
              )}

              {/* Cash Flow Forecast */}
              {cashFlowAnalysis.cashFlowForecast && cashFlowAnalysis.cashFlowForecast.length > 0 && (
                <Box>
                  <Text fontWeight="bold" mb={4}>3-Month Cash Flow Forecast</Text>
                  <VStack spacing={3} align="stretch">
                    {cashFlowAnalysis.cashFlowForecast.map((forecast, index) => (
                      <Card key={index} variant="outline" p={4}>
                        <Grid templateColumns="1fr auto" gap={4}>
                          <Box>
                            <Text fontWeight="bold">{forecast.date}</Text>
                            <Text color="gray.500">
                              Predicted: {formatCurrency(forecast.predictedAmount)}
                            </Text>
                            <Text fontSize="sm" color="gray.400">
                              Confidence: {formatCurrency(forecast.confidenceInterval[0])} - {formatCurrency(forecast.confidenceInterval[1])}
                            </Text>
                          </Box>
                          <VStack align="end" spacing={1}>
                            {forecast.contributingFactors.map((factor, idx) => (
                              <Badge key={idx} colorScheme="blue" size="sm">
                                {factor}
                              </Badge>
                            ))}
                          </VStack>
                        </Grid>
                      </Card>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* Risk Factors */}
              {cashFlowAnalysis.riskFactors && cashFlowAnalysis.riskFactors.length > 0 && (
                <Box>
                  <Text fontWeight="bold" mb={4}>Risk Factors</Text>
                  <VStack spacing={2} align="stretch">
                    {cashFlowAnalysis.riskFactors.map((risk, index) => (
                      <Alert key={index} status="warning" borderRadius="md">
                        <AlertIcon />
                        <Text>{risk}</Text>
                      </Alert>
                    ))}
                  </VStack>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* GST Compliance Analysis */}
      {gstComplianceAnalysis && (
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={8}>
          <CardHeader>
            <Heading size="md">GST Compliance Analysis</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={6} align="stretch">
              {/* GST Overview */}
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
                <Stat>
                  <StatLabel>GST Collected</StatLabel>
                  <StatNumber color="green.600">{formatCurrency(gstComplianceAnalysis.totalGstCollected)}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>GST Paid</StatLabel>
                  <StatNumber color="blue.600">{formatCurrency(gstComplianceAnalysis.totalGstPaid)}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Net GST Liability</StatLabel>
                  <StatNumber color={gstComplianceAnalysis.netGstLiability >= 0 ? "red.600" : "green.600"}>
                    {formatCurrency(gstComplianceAnalysis.netGstLiability)}
                  </StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Compliance Score</StatLabel>
                  <StatNumber>
                    <Progress 
                      value={gstComplianceAnalysis.complianceScore} 
                      colorScheme={
                        gstComplianceAnalysis.complianceScore >= 90 ? "green" :
                        gstComplianceAnalysis.complianceScore >= 70 ? "yellow" : "red"
                      }
                      size="sm"
                      borderRadius="md"
                    />
                    <Text fontSize="sm" mt={1}>{gstComplianceAnalysis.complianceScore.toFixed(1)}%</Text>
                  </StatNumber>
                </Stat>
              </SimpleGrid>

              {/* Compliance Status */}
              <Box>
                <HStack justify="space-between" mb={4}>
                  <Text fontWeight="bold">Compliance Status</Text>
                  <Badge 
                    colorScheme={
                      gstComplianceAnalysis.complianceStatus === "COMPLIANT" ? "green" :
                      gstComplianceAnalysis.complianceStatus === "WARNING" ? "yellow" :
                      gstComplianceAnalysis.complianceStatus === "NON_COMPLIANT" ? "red" : "gray"
                    }
                    size="lg"
                  >
                    {gstComplianceAnalysis.complianceStatus}
                  </Badge>
                </HStack>
              </Box>

              {/* GST Returns Due */}
              {gstComplianceAnalysis.gstReturnsDue && gstComplianceAnalysis.gstReturnsDue.length > 0 && (
                <Box>
                  <Text fontWeight="bold" mb={4}>GST Returns Due</Text>
                  <VStack spacing={3} align="stretch">
                    {gstComplianceAnalysis.gstReturnsDue.map((gstReturn, index) => (
                      <Card key={index} variant="outline" p={4}>
                        <Grid templateColumns="1fr auto" gap={4}>
                          <Box>
                            <Text fontWeight="bold">Period: {gstReturn.period}</Text>
                            <Text color="gray.500">Due Date: {gstReturn.due_date}</Text>
                            <Text mt={2}>GST Amount: {formatCurrency(gstReturn.gst_amount)}</Text>
                          </Box>
                          <VStack align="end" spacing={2}>
                            <Badge colorScheme="orange">{gstReturn.status}</Badge>
                          </VStack>
                        </Grid>
                      </Card>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* GST Penalties */}
              {gstComplianceAnalysis.gstPenalties && gstComplianceAnalysis.gstPenalties.length > 0 && (
                <Box>
                  <Text fontWeight="bold" mb={4}>Potential Penalties</Text>
                  <VStack spacing={3} align="stretch">
                    {gstComplianceAnalysis.gstPenalties.map((penalty, index) => (
                      <Alert key={index} status="error" borderRadius="md">
                        <AlertIcon />
                        <Box flex="1">
                          <AlertTitle>{penalty.type}</AlertTitle>
                          <AlertDescription>
                            {penalty.description} - Amount: {formatCurrency(penalty.amount)}
                          </AlertDescription>
                        </Box>
                        <Badge colorScheme="red">{penalty.severity}</Badge>
                      </Alert>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* GST Recommendations */}
              {gstComplianceAnalysis.gstRecommendations && gstComplianceAnalysis.gstRecommendations.length > 0 && (
                <Box>
                  <Text fontWeight="bold" mb={4}>Recommendations</Text>
                  <VStack spacing={2} align="stretch">
                    {gstComplianceAnalysis.gstRecommendations.map((recommendation, index) => (
                      <Alert key={index} status="info" borderRadius="md">
                        <AlertIcon />
                        <Text>{recommendation}</Text>
                      </Alert>
                    ))}
                  </VStack>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Recent Invoices */}
      <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={8}>
        <CardHeader>
          <Heading size="md">Recent Invoices</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {recentInvoices.map((invoice) => (
              <Card key={invoice.id} variant="outline" p={4}>
                <Grid templateColumns="1fr auto" gap={4}>
                  <Box>
                    <HStack spacing={4}>
                      <Text fontWeight="bold">{invoice.invoice_number}</Text>
                      <Badge colorScheme={getStatusColor(invoice.status)}>
                        {invoice.status}
                      </Badge>
                    </HStack>
                    <Text color="gray.500" mt={1}>
                      {invoice.vendor}
                    </Text>
                    <Text mt={2}>
                      Amount: {formatCurrency(invoice.amount)}
                    </Text>
                  </Box>
                  <VStack align="end" spacing={2}>
                    <Text color="gray.500">
                      {new Date(invoice.date).toLocaleDateString()}
                    </Text>
                    <Button
                      as={RouterLink}
                      to={`/invoices/${invoice.id}`}
                      size="sm"
                      variant="outline"
                    >
                      View Details
                    </Button>
                  </VStack>
                </Grid>
              </Card>
            ))}
          </VStack>
        </CardBody>
      </Card>

      {/* Service Status */}
      <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
        <CardHeader>
          <Heading size="md">Service Status</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <HStack justify="space-between">
              <HStack>
                <Icon as={FiCheckCircle} color="green.500" />
                <Text>OCR Service</Text>
              </HStack>
              <Badge colorScheme="green">Operational</Badge>
            </HStack>
            <HStack justify="space-between">
              <HStack>
                <Icon as={FiCheckCircle} color="green.500" />
                <Text>GST Categorization</Text>
              </HStack>
              <Badge colorScheme="green">Operational</Badge>
            </HStack>
            <HStack justify="space-between">
              <HStack>
                <Icon as={FiCheckCircle} color="green.500" />
                <Text>Reconciliation</Text>
              </HStack>
              <Badge colorScheme="green">Operational</Badge>
            </HStack>
            <HStack justify="space-between">
              <HStack>
                <Icon as={FiCheckCircle} color="green.500" />
                <Text>Fraud Detection</Text>
              </HStack>
              <Badge colorScheme="green">Operational</Badge>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  );
};

export default Dashboard; 