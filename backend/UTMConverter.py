from math import pi
from math import sin
from math import cos
from math import tan
from math import sqrt

class UTMConverter:
	sm_a = 6378137.0;
	sm_b = 6356752.314;
	sm_EccSquared = 6.69437999013e-03;
	UTMScaleFactor = 0.9996;

	def __init__(self):
		pass

	@staticmethod
	def deg2Rad(degrees): 
		return degrees * pi / 180.0;

	@staticmethod
	def rad2Deg(radians): 
		return radians * 180.0 / pi;

	@staticmethod
	def UTMCentralMeridian(zone):
		return UTMConverter.deg2Rad(-183.0 + (zone * 6.0));

	@staticmethod
	def footpointLatitude(y):
		n = (UTMConverter.sm_a - UTMConverter.sm_b) / (UTMConverter.sm_a + UTMConverter.sm_b);
		alpha_ = ((UTMConverter.sm_a + UTMConverter.sm_b) / 2.0) \
			* (1 + (pow(n, 2.0) / 4) + (pow(n, 4.0) / 64));
		y_ = y / alpha_;
		beta_ = (3.0 * n / 2.0) + (-27.0 * pow(n, 3.0) / 32.0) + (269.0 * pow(n, 5.0) / 512.0);
		gamma_ = (21.0 * pow(n, 2.0) / 16.0) + (-55.0 * pow(n, 4.0) / 32.0);
		delta_ = (151.0 * pow(n, 3.0) / 96.0) + (-417.0 * pow(n, 5.0) / 128.0);
		epsilon_ = (1097.0 * pow(n, 4.0) / 512.0);
		return y_ + (beta_ * sin(2.0 * y_)) \
			+ (gamma_ * sin(4.0 * y_)) \
			+ (delta_ * sin(6.0 * y_)) \
			+ (epsilon_ * sin(8.0 * y_));

	@staticmethod
	def mapXYToLatLon(x, y, lambda0):
		phif = UTMConverter.footpointLatitude(y);
		ep2 = (pow(UTMConverter.sm_a, 2.0) - pow(UTMConverter.sm_b, 2.0)) \
			/ pow(UTMConverter.sm_b, 2.0);
		cf = cos(phif);
		nuf2 = ep2 * pow(cf, 2.0);
		Nf = pow(UTMConverter.sm_a, 2.0) / (UTMConverter.sm_b * sqrt(1 + nuf2));
		Nfpow = Nf;
		tf = tan(phif);
		tf2 = tf * tf;
		tf4 = tf2 * tf2;
		x1frac = 1.0 / (Nfpow * cf);  
		Nfpow = Nfpow * Nf; 
		x2frac = tf / (2.0 * Nfpow);  
		Nfpow = Nfpow * Nf;
		x3frac = 1.0 / (6.0 * Nfpow * cf);      
		Nfpow = Nfpow * Nf;
		x4frac = tf / (24.0 * Nfpow);
		Nfpow = Nfpow * Nf;
		x5frac = 1.0 / (120.0 * Nfpow * cf);
		Nfpow = Nfpow * Nf;
		x6frac = tf / (720.0 * Nfpow);
		Nfpow = Nfpow * Nf;
		x7frac = 1.0 / (5040.0 * Nfpow * cf);
		Nfpow = Nfpow * Nf;
		x8frac = tf / (40320.0 * Nfpow);
		x2poly = -1.0 - nuf2;
		x3poly = -1.0 - 2 * tf2 - nuf2;
		x4poly = 5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 \
			- 3.0 * (nuf2 *nuf2) - 9.0 * tf2 * (nuf2 * nuf2);
		x5poly = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2;
		x6poly = -61.0 - 90.0 * tf2 - 45.0 * tf4 - 107.0 * nuf2 + 162.0 * tf2 * nuf2;
		x7poly = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2);
		x8poly = 1385.0 + 3633.0 * tf2 + 4095.0 * tf4 + 1575 * (tf4 * tf2);
		# Calculate latitude 
		philambda0 = UTMConverter.rad2Deg(phif + x2frac * x2poly * (x * x) \
			+ x4frac * x4poly * pow(x, 4.0)
			+ x6frac * x6poly * pow(x, 6.0)
			+ x8frac * x8poly * pow(x, 8.0));
		# Calculate longitude 
		philambda1 = UTMConverter.rad2Deg(lambda0 + x1frac * x \
			+ x3frac * x3poly * pow(x, 3.0) \
			+ x5frac * x5poly * pow(x, 5.0) \
			+ x7frac * x7poly * pow(x, 7.0));

		return (philambda0, philambda1);

	@staticmethod
	def UTMXYToLatLon(x, y, zone, southhemi):
		x = x - 500000.0;
		x = x / UTMConverter.UTMScaleFactor;
		if southhemi: 
			y = y - 10000000.0;
		y = y / UTMConverter.UTMScaleFactor
		cmeridian = UTMConverter.UTMCentralMeridian (zone);
		return UTMConverter.mapXYToLatLon (x, y, cmeridian);