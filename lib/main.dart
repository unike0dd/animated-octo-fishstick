
import 'package:flutter/material.dart';
import 'screens/product_list_screen.dart';
import 'screens/product_detail_screen.dart';
import 'screens/cart_screen.dart';
import 'screens/checkout_screen.dart';
import 'models/product.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'E-Commerce App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => ProductListScreen(),
        '/product-detail': (context) => ProductDetailScreen(product: ModalRoute.of(context)!.settings.arguments as Product),
        '/cart': (context) => CartScreen(),
        '/checkout': (context) => CheckoutScreen(),
      },
    );
  }
}
