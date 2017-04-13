#! /usr/bin/env bash


srcprefix="$HOME/src"
logfile='perfs.csv'
timeitlogfile='timeit.csv'
timefmt="%D;%F;%I;%K;%M;%O;%P;%R;%S;%U;%W;%X;%Z;%c;%e;%k;%p;%r;%s;%t;%w;%x"

commits=(
'40c67da4ccf8'  # reference implementation
'cebbabb56326'  # wrapped new API
'484e302528a6'  # pure new API
)


tmpdir=$(mktemp -p /tmp -d "perftest.XXXXXXXXXX")
pushd "$tmpdir"

for commit in ${commits[@]}
do
	# create venv
	commitdir="$commit.venv3"	
	python3 -m venv "$commitdir"
	pushd "$commitdir"
	source bin/activate  # activate venv

	# get sources
	mkdir src
	pushd src
	git clone "$srcprefix/evalys.git" evalys.git
	pushd evalys.git
	git checkout -q --detach "$commit"
	popd  # evalys.git
	if [ "$commit" != '40c67da4ccf8' ]
	then
		git clone "$srcprefix/procset.git" procset.git
		python -m pip install -U -e procset.git
	else
		git clone "$srcprefix/interval_set.git" interval_set.git
		python -m pip install -U -e interval_set.git
	fi
	python -m pip install -U -e evalys.git
	popd  # src

	# evaluate things
	echo 'method;trace;commit;id;D;F;I;K;M;O;P;R;S;U;W;X;Z;c;e;k;p;r;s;t;w;x' > "$logfile"
	echo 'method;trace;commit;id;nbiter;pytimeit' > "$timeitlogfile"
	traces=(
	"src/evalys.git/examples/jobs.csv"
	"src/evalys.git/tests/batsim_out_jobs.csv"
	)
	for trace in ${traces[@]}
	do
		for id in $(seq 1 30)
		do
			# basic evaluation: gantt
			columns="gantt;$(basename "$trace");$commit;$id;$timefmt"
			/usr/bin/time -f "$columns" -a -o "$logfile" evalys -g -o /tmp/figure.pdf "$trace"

			# basic evaluation: load
			columns="load;$(basename "$trace");$commit;$id;$timefmt"
			/usr/bin/time -f "$columns" -a -o "$logfile" python "src/evalys.git/examples/bleuse/example_load.py" -o /tmp/figure.pdf "$trace"

			# timeit evaluation
			for method in 'detailed_utilisation' 'free_slots'
			do
				columns="$method;$(basename "$trace");$commit;$id;$timefmt"
				/usr/bin/time -f "$columns" -a -o "$logfile" \
					python "$srcprefix/evalys.git/examples/bleuse/profiling/timeit_perf.py" -n30 "$method" "$trace" | \
					sed "s/^\([^;]*\);/\1;$(basename "$trace");$commit;$id;/" >> "$timeitlogfile"
			done
		done
	done

	# delete venv
	popd  # $commitdir
	deactivate
done

popd  # $tmpdir
