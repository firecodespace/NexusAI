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
} from '@chakra-ui/react';
import { FiUpload, FiFileText, FiRefreshCw } from 'react-icons/fi';
import { Link as RouterLink } from 'react-router-dom';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalInvoices: 0,
    processedInvoices: 0,
    totalAmount: 0,
    pendingValidation: 0,
  });
  const [recentInvoices, setRecentInvoices] = useState([]);
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
      
      const response = await fetch('http://localhost:8000/api/invoices/dashboard');
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
    <Box>
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
        >
          Upload Invoice
        </Button>
        <Button
          as={RouterLink}
          to="/invoices"
          leftIcon={<Icon as={FiFileText} />}
          variant="outline"
        >
          View All Invoices
        </Button>
      </HStack>

      {/* Statistics */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Total Invoices</StatLabel>
              <StatNumber>{stats.totalInvoices}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                23.36%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Processed</StatLabel>
              <StatNumber>{stats.processedInvoices}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                9.05%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Total Amount</StatLabel>
              <StatNumber>${stats.totalAmount.toLocaleString()}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                14.05%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Pending Validation</StatLabel>
              <StatNumber>{stats.pendingValidation}</StatNumber>
              <StatHelpText>
                <StatArrow type="decrease" />
                3.05%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Recent Invoices */}
      <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
        <CardHeader>
          <Heading size="md">Recent Invoices</Heading>
        </CardHeader>
        <CardBody>
          {recentInvoices.length === 0 ? (
            <Text color="gray.500">No recent invoices</Text>
          ) : (
            <VStack spacing={4} align="stretch">
              {recentInvoices.map((invoice) => (
                <Box
                  key={invoice.id}
                  p={4}
                  borderWidth="1px"
                  borderRadius="md"
                  borderColor={borderColor}
                  _hover={{ bg: hoverBg }}
                >
                  <Grid templateColumns="repeat(4, 1fr)" gap={4}>
                    <Text fontWeight="bold">{invoice.invoice_number}</Text>
                    <Text>{invoice.vendor}</Text>
                    <Text>${invoice.amount.toLocaleString()}</Text>
                    <Text color={invoice.status === 'processed' ? 'green.500' : 'yellow.500'}>
                      {invoice.status}
                    </Text>
                  </Grid>
                </Box>
              ))}
            </VStack>
          )}
        </CardBody>
        <CardFooter>
          <Button
            as={RouterLink}
            to="/invoices"
            variant="ghost"
            colorScheme="blue"
            size="sm"
          >
            View All Invoices
          </Button>
        </CardFooter>
      </Card>
    </Box>
  );
};

export default Dashboard; 