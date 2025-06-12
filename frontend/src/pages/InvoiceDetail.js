import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Card,
  CardBody,
  Grid,
  GridItem,
  Button,
  useColorModeValue,
  Spinner,
} from '@chakra-ui/react';
import { FiDownload, FiEdit2 } from 'react-icons/fi';

const InvoiceDetail = () => {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const fetchInvoiceDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/invoices/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch invoice details');
      }
      const data = await response.json();
      setInvoice(data);
    } catch (error) {
      console.error('Error fetching invoice details:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoiceDetails();
  }, [id]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Text color="red.500">Error: {error}</Text>
      </Box>
    );
  }

  if (!invoice) {
    return (
      <Box p={4}>
        <Text>Invoice not found</Text>
      </Box>
    );
  }

  return (
    <Box>
      <HStack justify="space-between" mb={6}>
        <Heading size="lg">Invoice Details</Heading>
        <HStack>
          <Button leftIcon={<FiEdit2 />} variant="outline">
            Edit
          </Button>
          <Button leftIcon={<FiDownload />} colorScheme="blue">
            Download
          </Button>
        </HStack>
      </HStack>

      <Grid templateColumns="repeat(2, 1fr)" gap={6}>
        <GridItem>
          <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontWeight="bold" color="gray.500">Invoice Number</Text>
                  <Text>{invoice.invoice_number}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">Date</Text>
                  <Text>{new Date(invoice.date).toLocaleDateString()}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">Status</Text>
                  <Badge colorScheme={invoice.status === 'processed' ? 'green' : 'yellow'}>
                    {invoice.status}
                  </Badge>
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </GridItem>

        <GridItem>
          <Card bg={cardBg} borderWidth="1px" borderColor={borderColor}>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontWeight="bold" color="gray.500">Vendor</Text>
                  <Text>{invoice.vendor}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">Amount</Text>
                  <Text>${invoice.amount.toLocaleString()}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">Due Date</Text>
                  <Text>{new Date(invoice.due_date).toLocaleDateString()}</Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default InvoiceDetail; 