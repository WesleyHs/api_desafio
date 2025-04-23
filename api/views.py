from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import bancoApi
from .serializers import DesafioSerializer
from datetime import datetime

class uploadView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.FILES:
                return Response({'mensagem': 'Nenhum arquivo localizado'}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            content = file.read().decode('utf-8').splitlines()
            
            results = {}
            
            for line in content:
                user_id = int(line[0:10].strip())
                name = line[10:55].strip()
                order_id = int(line[55:65].strip())
                product_id = int(line[65:75].strip())
                value = float(line[75:87].strip())
                date = line[-8:].strip()
                
                if user_id not in results:
                    results[user_id] = {
                        'user_id': user_id,
                        'name': name,
                        'orders': {}
                    }
                
                if order_id not in results[user_id]['orders']:
                    results[user_id]['orders'][order_id] = {
                        'order_id': order_id,
                        'total': 0,
                        'date': datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d'),
                        'products': []
                    }
                
                product = {
                    'product_id': product_id,
                    'value': f"{value:.2f}"
                }
                results[user_id]['orders'][order_id]['products'].append(product)
                results[user_id]['orders'][order_id]['total'] += value
            
            final_results = []
            for user_data in results.values():
                user_data['orders'] = list(user_data['orders'].values())
                for order in user_data['orders']:
                    order['total'] = f"{order['total']:.2f}"
                final_results.append(user_data)
            
            for result in final_results:
                serializer = DesafioSerializer(data=result)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(final_results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erro': str(e), 'mensagem': 'Erro ao carregar arquivo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class allView(generics.ListAPIView):
    queryset = bancoApi.objects.all()
    serializer_class = DesafioSerializer

class orderView(APIView):
    def get(self, request, order_id):
        try:
            data = bancoApi.objects.all()
            
            results = {}
            for index in data:
                for order in index.orders:
                    if order['order_id'] == order_id:
                        results = {
                            'user_id': index.user_id,
                            'name': index.name,
                            'orders': [order]
                        }
                        break
                        
            if not results:
                return Response({'error': 'Pedido não existe'}, status=status.HTTP_404_NOT_FOUND)
                
            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'erro': str(e), 'mensagem': 'Erro ao processar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class dateView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'error': 'periodo de data não informado'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date, '%Y%m%d')
            end_date = datetime.strptime(end_date, '%Y%m%d')

            data = bancoApi.objects.all()
            results = []

            for index in data:
                filter = []
                for order in index.orders:
                    order_date = datetime.strptime(order['date'], '%Y-%m-%d')
                    if order_date >= start_date and order_date <= end_date:
                        filter.append(order)
                
                if filter:
                    results.append({
                        'user_id': index.user_id,
                        'name': index.name,
                        'orders': filter
                    })

            if not results:
                return Response({'message': 'Não existe pedidos nesse periodo'}, status=status.HTTP_404_NOT_FOUND)

            return Response(results, status=status.HTTP_200_OK)

        except ValueError:
            return Response({'error': 'Formato de data invalido. Utilize YYYYMMDD'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'erro': str(e), 'mensagem': 'Erro ao processar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

