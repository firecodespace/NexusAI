import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Input,
  Select,
  HStack,
  Text,
  Badge,
  useColorModeValue,
  InputGroup,
  InputLeftElement,
  Flex,
  Spinner,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { FiSearch, FiFilter, FiDownload, FiEye } from 'react-icons/fi';
import { Link as RouterLink } from 'react-router-dom';

const InvoiceList = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const toast = useToast();

  const fetchInvoices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/invoices?page=${currentPage}&sort=${sortField}&direction=${sortDirection}&status=${statusFilter}`
      );
      if (!response.ok) {
        throw new Error('Failed to fetch invoices');
      }
      const data = await response.json();
      setInvoices(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      setError(error.message);
      toast({
        title: 'Error',
        description: 'Failed to fetch invoices',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  }, [currentPage, sortField, sortDirection, statusFilter, toast]);

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleDownload = async (invoiceId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/invoices/${invoiceId}/download`);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice-${invoiceId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      toast({
        title: 'Download Error',
        description: 'Failed to download invoice',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      processed: 'green',
      pending: 'yellow',
      error: 'red',
      validating: 'blue',
    };
    return colors[status] || 'gray';
  };

  const filteredInvoices = invoices ? invoices.filter((invoice) =>
    Object.values(invoice).some((value) =>
      value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
    )
  ) : [];

  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.700');

  if (error) {
    return (
      <Box p={4}>
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          <Box flex="1">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Heading size="lg" mb={6}>Invoices</Heading>

      {/* Filters and Search */}
      <HStack spacing={4} mb={6}>
        <InputGroup maxW="400px">
          <InputLeftElement pointerEvents="none">
            <FiSearch color="gray.300" />
          </InputLeftElement>
          <Input
            placeholder="Search invoices..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>

        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          maxW="200px"
        >
          <option value="all">All Status</option>
          <option value="processed">Processed</option>
          <option value="pending">Pending</option>
          <option value="error">Error</option>
          <option value="validating">Validating</option>
        </Select>
      </HStack>

      {/* Invoices Table */}
      <Box
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        bg={bgColor}
        borderColor={borderColor}
      >
        {loading ? (
          <Flex justify="center" align="center" p={8}>
            <Spinner size="xl" />
          </Flex>
        ) : (
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th cursor="pointer" onClick={() => handleSort('invoice_number')}>
                  Invoice Number
                </Th>
                <Th cursor="pointer" onClick={() => handleSort('date')}>
                  Date
                </Th>
                <Th cursor="pointer" onClick={() => handleSort('vendor')}>
                  Vendor
                </Th>
                <Th cursor="pointer" onClick={() => handleSort('amount')}>
                  Amount
                </Th>
                <Th cursor="pointer" onClick={() => handleSort('status')}>
                  Status
                </Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredInvoices.map((invoice) => (
                <Tr key={invoice.id}>
                  <Td>{invoice.invoice_number}</Td>
                  <Td>{new Date(invoice.date).toLocaleDateString()}</Td>
                  <Td>{invoice.vendor}</Td>
                  <Td>${invoice.amount.toLocaleString()}</Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(invoice.status)}>
                      {invoice.status}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <Button
                        as={RouterLink}
                        to={`/invoices/${invoice.id}`}
                        size="sm"
                        leftIcon={<FiEye />}
                        variant="ghost"
                      >
                        View
                      </Button>
                      <Button
                        size="sm"
                        leftIcon={<FiDownload />}
                        variant="ghost"
                        onClick={() => handleDownload(invoice.id)}
                      >
                        Download
                      </Button>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Box>

      {/* Pagination */}
      <HStack spacing={4} mt={4} justify="center">
        <Button
          onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          isDisabled={currentPage === 1}
        >
          Previous
        </Button>
        <Text>Page {currentPage}</Text>
        <Button
          onClick={() => setCurrentPage((prev) => prev + 1)}
          isDisabled={invoices.length < itemsPerPage}
        >
          Next
        </Button>
      </HStack>
    </Box>
  );
};

export default InvoiceList; 